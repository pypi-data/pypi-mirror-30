def openbis_definitions(entity):
    entities = {
        "Space": {
            "attrs_new": "code description".split(),
            "attrs_up": "description".split(),
            "attrs": "code permId description registrator registrationDate modificationDate".split(),
            "multi": "".split(),
            "identifier": "spaceId",
        },
        "Project": {
            "attrs_new": "code description space attachments".split(),
            "attrs_up": "description space attachments".split(),
            "attrs": "code description permId identifier space leader registrator registrationDate modifier modificationDate attachments".split(),
            "multi": "".split(),
            "identifier": "projectId",
        },
        "Experiment": {
            "attrs_new": "code type project tags attachments".split(),
            "attrs_up": "project tags attachments".split(),
            "attrs": "code permId identifier type project tags attachments".split(),
            "multi": "tags attachments".split(),
            "identifier": "experimentId",
        },
        "Sample": {
            "attrs_new": "code type parents children space experiment tags attachments".split(),
            "attrs_up": "parents children space experiment tags attachments".split(),
            "attrs": "code permId identifier type parents children components space experiment tags attachments".split(),
            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'childIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
            },
            "identifier": "sampleId",
            "cre_type": "as.dto.sample.create.SampleCreation",
            "multi": "parents children components tags attachments".split(),
        },
        "SemanticAnnotation": {
            "attrs_new": "permId entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId".split(),
            "attrs_up": "entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId ".split(),
            "attrs": "permId entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId creationDate".split(),
            "ids2type": {
                "propertyTypeId": { 
                    "permId": "as.dto.property.id.PropertyTypePermId"
                },
                "entityTypeId": { 
                    "permId": "as.dto.entity.id.EntityTypePermId"
                },
            },
            "identifier": "permId",
            "cre_type": "as.dto.sample.create.SampleCreation",
            "multi": "parents children components tags attachments".split(),
        },
        "DataSet": {
            "attrs_new": "type experiment sample parents children components tags".split(),
            "attrs_up": "parents children experiment sample components tags".split(),
            "attrs": "code permId type experiment sample parents children components tags accessDate dataProducer dataProductionDate registrator registrationDate modifier modificationDate dataStore measured".split(),

            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'childIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'containerIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
            },
            "multi": "parents children container".split(),
            "identifier": "dataSetId",
        },
        "Material": {
            "attrs_new": "code description type creation tags".split(),
            "attrs_up": "description type creation tags".split(),
            "attrs": "code description type creation registrator tags".split(),
            "multi": "".split(),
            "identifier": "materialId",
        },
        "Tag": {
            "attrs_new": "code description".split(),
            "attrs_up": "description".split(),
            "attrs": "permId code description registrationDate".split(),
            "multi": "".split(),
            "identifier": "tagId",
        },
        "Plugin": {
            "attrs_new": "name description available script available script pluginType pluginKind entityKinds".split(),
            "attrs_up": "description, available script available script pluginType pluginKind entityKinds".split(),
            "attrs": "permId name description registrator registrationDate available script pluginType pluginKind entityKinds".split(),
            "multi": "".split(),
            "identifier": "pluginId",
        },
        "Person": {
            "attrs_new": "userId space".split(),
            "attrs_up": "space".split(),
            "attrs": "permId userId firstName lastName email space registrationDate ".split(),
            "multi": "".split(),
            "identifier": "userId",
        },
        "AuthorizationGroup" : {
            "attrs_new": "code description userIds".split(),
            "attrs_up": "code description userIds".split(),
            "attrs": "permId code description registrator registrationDate modificationDate users".split(),
            "multi": "users".split(),
            "identifier": "groupId",
        },
        "RoleAssignment" : {
            "attrs": "id user authorizationGroup role roleLevel space project registrator registrationDate".split(),
            "attrs_new": "role roleLevel user authorizationGroup role space project".split(),
        },
        "attr2ids": {
            "space": "spaceId",
            "project": "projectId",
            "sample": "sampleId",
            "samples": "sampleIds",
            "dataSet": "dataSetId",
            "dataSets": "dataSetIds",
            "experiment": "experimentId",
            "experiments": "experimentIds",
            "material": "materialId",
            "materials": "materialIds",
            "container": "containerId",
            "component": "componentId",
            "components": "componentIds",
            "parents": "parentIds",
            "children": "childIds",
            "tags": "tagIds",
            "userId": "userId",
            "users": "userIds",
            "description": "description",
        },
        "ids2type": {
            'spaceId': {'permId': {'@type': 'as.dto.space.id.SpacePermId'}},
            'projectId': {'permId': {'@type': 'as.dto.project.id.ProjectPermId'}},
            'experimentId': {'permId': {'@type': 'as.dto.experiment.id.ExperimentPermId'}},
            'tagIds': {'code': {'@type': 'as.dto.tag.id.TagCode'}},
        },
    }
    return entities[entity]


fetch_option = {
    "space": {"@type": "as.dto.space.fetchoptions.SpaceFetchOptions"},
    "project": {"@type": "as.dto.project.fetchoptions.ProjectFetchOptions"},
    "person": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "users": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "user": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "owner": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "registrator": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "modifier": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "leader": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "authorizationGroup": {"@type": "as.dto.authorizationgroup.fetchoptions.AuthorizationGroupFetchOptions"},
    "experiment": {
        "@type": "as.dto.experiment.fetchoptions.ExperimentFetchOptions",
        "type": {"@type": "as.dto.experiment.fetchoptions.ExperimentTypeFetchOptions"}
    },
    "sample": {
        "@type": "as.dto.sample.fetchoptions.SampleFetchOptions",
        "type": {"@type": "as.dto.sample.fetchoptions.SampleTypeFetchOptions"}
    },
    "samples": {"@type": "as.dto.sample.fetchoptions.SampleFetchOptions"},
    "dataSets": {
        "@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions",
        "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
        "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"},
    },
    "physicalData": {"@type": "as.dto.dataset.fetchoptions.PhysicalDataFetchOptions"},
    "linkedData": {
        "externalDms": {"@type": "as.dto.externaldms.fetchoptions.ExternalDmsFetchOptions"},
        "@type": "as.dto.dataset.fetchoptions.LinkedDataFetchOptions"
    },
    "roleAssignments": {
        "@type": "as.dto.roleassignment.fetchoptions.RoleAssignmentFetchOptions",
        "space": {
            "@type": "as.dto.space.fetchoptions.SpaceFetchOptions"
        }
    },
    "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
    "propertyAssignments": {
        "@type": "as.dto.property.fetchoptions.PropertyAssignmentFetchOptions",
        "propertyType": {
            "@type": "as.dto.property.fetchoptions.PropertyTypeFetchOptions",
            "vocabulary": {
                "@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions",
            }
        }
    },
    "tags": {"@type": "as.dto.tag.fetchoptions.TagFetchOptions"},
    "tag": {"@type": "as.dto.tag.fetchoptions.TagFetchOptions"},
    "attachments": {"@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions"},
    "attachmentsWithContent": {
        "@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions",
        "content": {
            "@type": "as.dto.common.fetchoptions.EmptyFetchOptions"
        },
    },
    "script": {
        "@type": "as.dto.common.fetchoptions.EmptyFetchOptions",
    },
    "history": {"@type": "as.dto.history.fetchoptions.HistoryEntryFetchOptions"},
    "dataStore": {"@type": "as.dto.datastore.fetchoptions.DataStoreFetchOptions"},
    "plugin": {"@type": "as.dto.plugin.fetchoptions.PluginFetchOptions"},
}
