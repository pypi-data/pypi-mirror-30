from pandas import DataFrame, Series
from tabulate import tabulate
from .definitions import openbis_definitions, fetch_option
from .utils import parse_jackson, check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl
from .attachment import Attachment

import copy
import base64
import os

class AttrHolder():
    """ General class for both samples and experiments that hold all common attributes, such as:
    - space
    - project
    - experiment (sample)
    - samples (experiment)
    - dataset
    - parents (sample, dataset)
    - children (sample, dataset)
    - tags
    """

    def __init__(self, openbis_obj, entity, type=None):
        self.__dict__['_openbis'] = openbis_obj
        self.__dict__['_entity'] = entity

        if type is not None:
            self.__dict__['_type'] = type.data

        self.__dict__['_allowed_attrs'] = openbis_definitions(entity)['attrs']
        self.__dict__['_identifier'] = None
        self.__dict__['_is_new'] = True
        self.__dict__['_tags'] = []

    def __call__(self, data):
        """This internal method is invoked when an existing object is loaded.
        Instead of invoking a special method we «call» the object with the data
           self(data)
        which automatically invokes this method.
        Since the data comes from openBIS, we do not have to check it (hence the
        self.__dict__ statements to prevent invoking the __setattr__ method)
        Internally data is stored with an underscore, e.g.
            sample._space = { 
                '@type': 'as.dto.space.id.SpacePermId',
                'permId': 'MATERIALS' 
            }
        but when fetching the attribute without the underscore, we only return
        the relevant data for the user:
            sample.space    # MATERIALS
        """
        # entity is read from openBIS, so it is not new anymore
        self.__dict__['_is_new'] = False

        for attr in self._allowed_attrs:
            if attr in ["code", "permId", "identifier",
                        "type", "container", "components"]:
                self.__dict__['_' + attr] = data.get(attr, None)
                # remove the @id attribute
                if isinstance(self.__dict__['_' + attr], dict):
                    self.__dict__['_' + attr].pop('@id')

            elif attr in ["space"]:
                d = data.get(attr, None)
                if d is not None:
                    d = d['permId']
                self.__dict__['_' + attr] = d

            elif attr in ["sample", "experiment", "project"]:
                d = data.get(attr, None)
                if d is not None:
                    d = d['identifier']
                self.__dict__['_' + attr] = d

            elif attr in ["parents", "children", "samples"]:
                self.__dict__['_' + attr] = []
                if data[attr] is not None:
                    for item in data[attr]:
                        if 'identifier' in item:
                            self.__dict__['_' + attr].append(item['identifier'])
                        elif 'permId' in item:
                            self.__dict__['_' + attr].append(item['permId'])

            elif attr in ["tags"]:
                tags = []
                for item in data[attr]:
                    tags.append({
                        "code": item['code'],
                        "@type": "as.dto.tag.id.TagCode"
                    })
                self.__dict__['_tags'] = tags
                self.__dict__['_prev_tags'] = copy.deepcopy(tags)
            else:
                self.__dict__['_' + attr] = data.get(attr, None)

    def _new_attrs(self, method_name=None):
        """Returns the Python-equivalent JSON request when a new object is created.
        It is used internally by the save() method of a newly created object.
        """
        defs = openbis_definitions(self.entity)
        attr2ids = openbis_definitions('attr2ids')

        new_obj = {
            "@type": "as.dto.{}.create.{}Creation".format(self.entity.lower(), self.entity)
        }

        for attr in defs['attrs_new']:
            items = None

            if attr == 'type':
                new_obj['typeId'] = self._type['permId']
                continue

            elif attr == 'attachments':
                attachments = getattr(self, '_new_attachments')
                if attachments is None:
                    continue
                atts_data = [attachment.get_data() for attachment in attachments]
                items = atts_data

            elif attr in defs['multi']:
                # parents, children, components, container, tags, attachments
                items = getattr(self, '_' + attr)
                if items is None:
                    items = []

            elif attr == 'userIds':
                if '_changed_users' not in self.__dict__:
                    continue

                new_obj[attr]=[]
                for userId in self.__dict__['_changed_users']:
                    if self.__dict__['_changed_users'][userId]['action'] == 'Add':
                        new_obj[attr].append({
                            "permId": userId,
                            "@type": "as.dto.person.id.PersonPermId"
                        })

            else:
                items = getattr(self, '_' + attr)

                key = None
                if attr in attr2ids:
                    # translate parents into parentIds, children into childIds etc.
                    key = attr2ids[attr]
                else:
                    key = attr

                new_obj[key] = items

        # guess the method name for creating a new entity and build the request
        if method_name is None:
            method_name = "create{}s".format(self.entity)
        request = {
            "method": method_name,
            "params": [
                self.openbis.token,
                [new_obj]
            ]
        }
        return request


    def _up_attrs(self, method_name=None):
        """Returns the Python-equivalent JSON request when a new object is updated.
        It is used internally by the save() method of an object to be updated.
        """
        defs = openbis_definitions(self._entity)
        attr2ids = openbis_definitions('attr2ids')

        up_obj = {
            "@type": "as.dto.{}.update.{}Update".format(self.entity.lower(), self.entity),
            defs["identifier"]: self._permId
        }

        # look at all attributes available for that entity
        # that can be updated
        for attr in defs['attrs_up']:
            items = None

            if attr == 'attachments':
                # v3 API currently only supports adding attachments
                attachments = self.__dict__.get('_new_attachments', None)
                if attachments is None:
                    continue
                atts_data = [attachment.get_data() for attachment in attachments]

                up_obj['attachments'] = {
                    "actions": [{
                        "items": atts_data,
                        "@type": "as.dto.common.update.ListUpdateActionAdd"
                    }],
                    "@type": "as.dto.attachment.update.AttachmentListUpdateValue"
                }

            elif attr == 'tags':
                # look which tags/users have been added or removed and update them

                if getattr(self, '_prev_'+attr) is None:
                    self.__dict__['_prev_'+attr] = []
                actions = []
                for id in self.get('_prev_'+attr):
                    if id not in self.get('_'+attr):
                        actions.append({
                            "items": [id],
                            "@type": "as.dto.common.update.ListUpdateActionRemove"
                        })

                for id in self.get('_'+attr):
                    if id not in self.get('_prev_'+attr):
                        actions.append({
                            "items": [id],
                            "@type": "as.dto.common.update.ListUpdateActionAdd"
                        })

                up_obj['tagIds'] = {
                    "@type": "as.dto.common.update.IdListUpdateValue",
                    "actions": actions
                }

            elif attr == 'userIds':
                actions = []
                if '_changed_users' not in self.__dict__:
                    continue
                for userId in self.__dict__['_changed_users']:
                    actions.append({
		        "items": [
                            {
                                "permId": userId,
                                "@type": "as.dto.person.id.PersonPermId"
			    }
                        ],
		        "@type": "as.dto.common.update.ListUpdateAction{}".format(
                            self.__dict__['_changed_users'][userId]['action']
                        )
		    })

                up_obj['userIds'] = {
                    "actions": actions,
                    "@type": "as.dto.common.update.IdListUpdateValue" 
                }

            elif attr == 'description':
                # alway update description
                up_obj['description'] = {
                    "value": self.__dict__['_description'],
                    "isModified": True,
                    "@type": "as.dto.common.update.FieldUpdateValue"
                }

            elif '_' + attr in self.__dict__:
                # handle multivalue attributes (parents, children, tags etc.)
                # we only cover the Set mechanism, which means we always update 
                # all items in a list
                if attr in defs['multi']:
                    items = self.__dict__.get('_' + attr, [])
                    if items == None:
                        items = []
                    up_obj[attr2ids[attr]] = {
                        "actions": [
                            {
                                "items": items,
                                "@type": "as.dto.common.update.ListUpdateActionSet",
                            }
                        ],
                        "@type": "as.dto.common.update.IdListUpdateValue"
                    }
                else:
                    # handle single attributes (space, experiment, project, container, etc.)
                    value = self.__dict__.get('_' + attr, {})
                    if value is None:
                        pass
                    elif len(value) == 0:
                        # value is {}: it means that we want this attribute to be
                        # deleted, not updated.
                        up_obj[attr2ids[attr]] = {
                            "@type": "as.dto.common.update.FieldUpdateValue",
                            "isModified": True,
                        }
                    elif 'isModified' in value and value['isModified'] == True:
                        val = {}
                        for x in ['identifier','permId','@type']:
                            if x in value:
                                val[x] = value[x]

                        up_obj[attr2ids[attr]] = {
                            "@type": "as.dto.common.update.FieldUpdateValue",
                            "isModified": True,
                            "value": val
                        }

        # update an existing entity
        if method_name is None:
            method_name = "update{}s".format(self.entity)
        request = {
            "method": method_name,
            "params": [
                self.openbis.token,
                [up_obj]
            ]
        }
        return request


    def __getattr__(self, name):
        """ handles all attribute requests dynamically.
        Values are returned in a sensible way, for example:
            the identifiers of parents, children and components are returned as an
            array of values, whereas attachments, users (of groups) and
            roleAssignments are returned as an array of dictionaries.
        """

        name_map = {
            'group': 'authorizationGroup',
            'roles': 'roleAssignments'
        }
        if name in name_map:
            name = name_map[name]

        int_name = '_' + name
        if int_name in self.__dict__:
            if int_name == '_attachments':
                attachments = []
                for att in self._attachments:
                    attachments.append({
                        "fileName":    att.get('fileName'),
                        "title":       att.get('title'),
                        "description": att.get('description'),
                        "version":     att.get('version'),
                    })
                return attachments

            elif int_name == '_users':
                users = []
                for user in self._users:
                    users.append({
                        "firstName": user.get('firstName'),
                        "lastName" : user.get('lastName'),
                        "email"    : user.get('email'),
                        "userId"   : user.get('userId'),
                        "space"    : user.get('space').get('code') if user.get('space') is not None else None,
                    })
                return users

            elif int_name == '_roleAssignments':
                ras = []
                for ra in self._roleAssignments:
                    ras.append({
                        "techId":        ra.get('id').get('techId'),
                        "role":      ra.get('role'),
                        "roleLevel": ra.get('roleLevel'),
                        "space":     ra.get('space').get('code'),
                        "project":   ra.get('role'),
                    })
                return ras

            elif int_name in ['_registrator', '_modifier', '_dataProducer']:
                return self.__dict__[int_name].get('userId', None)

            elif int_name in ['_registrationDate', '_modificationDate', '_accessDate', '_dataProductionDate']:
                return format_timestamp(self.__dict__[int_name])

            # if the attribute contains a list, 
            # return a list of either identifiers, codes or
            # permIds (whatever is available first)
            elif isinstance(self.__dict__[int_name], list):
                values = []
                for item in self.__dict__[int_name]:
                    if "identifier" in item:
                        values.append(item['identifier'])
                    elif "code" in item:
                        values.append(item['code'])
                    elif "userId" in item:
                        values.append(item['userId'])
                    elif "permId" in item:
                        values.append(item['permId'])
                    else:
                        pass
                return values

            # attribute contains a dictionary: same procedure as above.
            elif isinstance(self.__dict__[int_name], dict):
                if "identifier" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['identifier']
                elif "code" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['code']
                elif "userId" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['userId']
                elif "permId" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['permId']
                elif "id" in self.__dict__[int_name]:
                    return self.__dict__[int_name]['id']

            else:
                return self.__dict__[int_name]
        else:
            return None

    def __setattr__(self, name, value):
        """This method is always invoked whenever we assign an attribute to an
        object, e.g.
            new_sample.space = 'MATERIALS'
            new_sample.parents = ['/MATERIALS/YEAST747']
        """
        #allowed_attrs = []
        #if self.is_new:
        #    allowed_attrs = openbis_definitions(self.entity)['attrs_new']
        #else:
        #    allowed_attrs = openbis_definitions(self.entity)['attrs_up']

        #if name not in allowed_attrs:
        #    raise ValueError("{} is not in the list of changeable attributes ({})".format(name, ", ".join(allowed_attrs) ) )

        if name in ["parents", "parent", "children", "child", "components"]:
            if name == "parent":
                name = "parents"
            if name == "child":
                name = "children"

            if not isinstance(value, list):
                value = [value]
            objs = []
            for val in value:
                if isinstance(val, str):
                    # fetch objects in openBIS, make sure they actually exists
                    obj = getattr(self._openbis, 'get_' + self._entity.lower())(val)
                    objs.append(obj)
                elif getattr(val, '_permId'):
                    # we got an existing object
                    objs.append(val)

            permids = []
            for item in objs:
                permid = item._permId
                # remove any existing @id keys to prevent jackson parser errors
                if '@id' in permid: permid.pop('@id')
                permids.append(permid)

            self.__dict__['_' + name] = permids
        elif name in ["tags"]:
            self.set_tags(value)

        elif name in ["users"]:
            self.set_users(value)

        elif name in ["attachments"]:
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.add_attachment(**item)
                    else:
                        self.add_attachment(item)

            else:
                self.add_attachment(value)

        elif name in ["space"]:
            obj = None
            if value is None:
                self.__dict__['_'+name] = None
                return

            if isinstance(value, str):
                # fetch object in openBIS, make sure it actually exists
                obj = getattr(self._openbis, "get_" + name)(value)
            else:
                obj = value

            self.__dict__['_' + name] = obj.data['permId']

            # mark attribute as modified, if it's an existing entity
            if self.is_new:
                pass
            else:
                self.__dict__['_' + name]['isModified'] = True

        elif name in ["sample", "experiment", "project"]:
            obj = None
            if isinstance(value, str):
                # fetch object in openBIS, make sure it actually exists
                obj = getattr(self._openbis, "get_" + name)(value)
            elif value is None:
                self.__dict__['_'+name] = {}
                return
            else:
                obj = value

            self.__dict__['_' + name] = obj.data['identifier']

            # mark attribute as modified, if it's an existing entity
            if self.is_new:
                pass
            else:
                self.__dict__['_' + name]['isModified'] = True

        elif name in ["identifier"]:
            raise KeyError("you can not modify the {}".format(name))
        elif name == "code":
            try:
                if self._type['autoGeneratedCode']:
                    raise KeyError("This {}Type has auto-generated code. You cannot set a code".format(self.entity))
            except KeyError:
                pass
            except TypeError:
                pass

            self.__dict__['_code'] = value

        elif name in ["userId", "description"]:
            # values that are directly assigned
            self.__dict__['_' + name] = value

        elif name in ["userIds"]:
            self.add_users(value)

        else:
            self.__dict__['_'+name] = value


    def get_type(self):
        return self._type

    def _ident_for_whatever(self, whatever):
        if isinstance(whatever, str):
            # fetch parent in openBIS, we are given an identifier
            obj = getattr(self._openbis, 'get_'+self._entity.lower())(whatever)
        else:
            # we assume we got an object
            obj = whatever

        ident = None
        if getattr(obj, '_identifier'):
            ident = obj._identifier
        elif getattr(obj, '_permId'):
            ident = obj._permId

        if '@id' in ident: ident.pop('@id')
        return ident

    def get_parents(self, **kwargs):
        identifier = self.identifier
        if identifier is None:
            identifier = self.permId

        if identifier is None:
            # TODO: if this is a new object, return the list of the parents which have been assigned
            pass
        else:
            return getattr(self._openbis, 'get_' + self._entity.lower() + 's')(withChildren=identifier, **kwargs)

    def add_parents(self, parents):
        if getattr(self, '_parents') is None:
            self.__dict__['_parents'] = []
        if not isinstance(parents, list):
            parents = [parents]
        for parent in parents:
            self.__dict__['_parents'].append(self._ident_for_whatever(parent))

    def del_parents(self, parents):
        if getattr(self, '_parents') is None:
            return
        if not isinstance(parents, list):
            parents = [parents]
        for parent in parents:
            ident = self._ident_for_whatever(parent)
            for i, item in enumerate(self.__dict__['_parents']):
                if 'identifier' in ident and 'identifier' in item and ident['identifier'] == item['identifier']:
                    self.__dict__['_parents'].pop(i)
                elif 'permId' in ident and 'permId' in item and ident['permId'] == item['permId']:
                    self.__dict__['_parents'].pop(i)

    def get_children(self, **kwargs):
        identifier = self.identifier
        if identifier is None:
            identifier = self.permId

        if identifier is None:
            # TODO: if this is a new object, return the list of the children which have been assigned
            pass
        else:
            # e.g. self._openbis.get_samples(withParents=self.identifier)
            return getattr(self._openbis, 'get_' + self._entity.lower() + 's')(withParents=identifier, **kwargs)

    def add_children(self, children):
        if getattr(self, '_children') is None:
            self.__dict__['_children'] = []
        if not isinstance(children, list):
            children = [children]
        for child in children:
            self.__dict__['_children'].append(self._ident_for_whatever(child))

    def del_children(self, children):
        if getattr(self, '_children') is None:
            return
        if not isinstance(children, list):
            children = [children]
        for child in children:
            ident = self._ident_for_whatever(child)
            for i, item in enumerate(self.__dict__['_children']):
                if 'identifier' in ident and 'identifier' in item and ident['identifier'] == item['identifier']:
                    self.__dict__['_children'].pop(i)
                elif 'permId' in ident and 'permId' in item and ident['permId'] == item['permId']:
                    self.__dict__['_children'].pop(i)

    @property
    def tags(self):
        if getattr(self, '_tags') is not None:
            return [x['code'] for x in self._tags]

    def set_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        tagIds = _create_tagIds(tags)

        # remove tags that are not in the new tags list
        for tagId in self.__dict__['_tags']:
            if tagId not in tagIds:
                self.__dict__['_tags'].remove(tagId)

        # add all new tags that are not in the list yet
        for tagId in tagIds:
            if tagId not in self.__dict__['_tags']:
                self.__dict__['_tags'].append(tagId)

    def set_users(self, userIds):
        if userIds is None:
            return
        if getattr(self, '_userIds') is None:
            self.__dict__['_userIds'] = []
        if not isinstance(userIds, list):
            userIds = [userIds]
        for userId in userIds:
            person = self.openbis.get_person(userId=user, only_data=True)
            self.__dict__['_userIds'].append({
                "permId": userId,
                "@type": "as.dto.person.id.PersonPermId"
            })
    set_members = set_users  # Alias

        
    def add_users(self, userIds):
        if userIds is None:
            return
        if getattr(self, '_changed_users') is None:
            self.__dict__['_changed_users'] = {}

        if not isinstance(userIds, list):
            userIds = [userIds]
        for userId in userIds:
            self.__dict__['_changed_users'][userId] = {
                "action": "Add"
            }
    add_members = add_users # Alias


    def del_users(self, userIds):
        if userIds is None:
            return
        if getattr(self, '_changed_users') is None:
            self.__dict__['_changed_users'] = {}

        if not isinstance(userIds, list):
            userIds = [userIds]
        for userId in userIds:
            self.__dict__['_changed_users'][userId] = {
                "action": "Remove"
            }
    del_members = del_users  # Alias

    def add_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        # add the new tags to the _tags and _new_tags list,
        # if not listed yet
        tagIds = _create_tagIds(tags)
        for tagId in tagIds:
            if not tagId in self.__dict__['_tags']:
                self.__dict__['_tags'].append(tagId)

    def del_tags(self, tags):
        if getattr(self, '_tags') is None:
            self.__dict__['_tags'] = []

        # remove the tags from the _tags and _del_tags list,
        # if listed there
        tagIds = _create_tagIds(tags)
        for tagId in tagIds:
            if tagId in self.__dict__['_tags']:
                self.__dict__['_tags'].remove(tagId)

    def get_attachments(self):
        if getattr(self, '_attachments') is None:
            return None
        else:
            return DataFrame(self._attachments)[['fileName', 'title', 'description', 'version']]

    def add_attachment(self, fileName, title=None, description=None):
        att = Attachment(filename=fileName, title=title, description=description)
        if getattr(self, '_attachments') is None:
            self.__dict__['_attachments'] = []
        self._attachments.append(att.get_data_short())

        if getattr(self, '_new_attachments') is None:
            self.__dict__['_new_attachments'] = []
        self._new_attachments.append(att)

    def download_attachments(self):
        method = 'get' + self.entity + 's'
        entity = self.entity.lower()
        request = {
            "method": method,
            "params": [
                self._openbis.token,
                [self._permId],
                dict(
                    attachments=fetch_option['attachmentsWithContent'],
                    **fetch_option[entity]
                )
            ]
        }
        resp = self._openbis._post_request(self._openbis.as_v3, request)
        attachments = resp[self.permId]['attachments']
        file_list = []
        for attachment in attachments:
            filename = os.path.join(
                self._openbis.hostname,
                self.permId,
                attachment['fileName']
            )
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as att:
                content = base64.b64decode(attachment['content'])
                att.write(content)
            file_list.append(filename)
        return file_list

    def _repr_html_(self):
        def nvl(val, string=''):
            if val is None:
                return string
            return val

        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self._allowed_attrs:
            if attr == 'attachments':
                continue
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, nvl(getattr(self, attr, ''), '')
            )
        if getattr(self, '_attachments') is not None:
            html += "<tr><td>attachments</td><td>"
            html += "<br/>".join(att['fileName'] for att in self._attachments)
            html += "</td></tr>"

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):
        """ When using iPython, this method displays a nice table
        of all attributes and their values when the object is printed.
        """

        headers = ['attribute', 'value']
        lines = []
        for attr in self._allowed_attrs:
            if attr == 'attachments':
                continue
            elif attr == 'users' and '_users' in self.__dict__:
                lines.append([
                    attr,
                    ", ".join(att['userId'] for att in self._users)
                ])
            elif attr == 'roleAssignments' and '_roleAssignments' in self.__dict__:
                roles = []
                for role in self._roleAssignments:
                    if role.get('space') is not None:
                        roles.append("{} ({})".format(
                            role.get('role'),
                            role.get('space').get('code')
                        ))
                    else:
                        roles.append(role.get('role'))

                lines.append([
                    attr,
                    ", ".join(roles)
                ])
                
            else:
                lines.append([
                    attr,
                    nvl(getattr(self, attr, ''))
                ])
        return tabulate(lines, headers=headers)
