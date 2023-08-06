from tabulate import tabulate

class Things():
    """An object that contains a DataFrame object about an entity  available in openBIS.
       
    """

    def __init__(self, openbis_obj, entity, df, identifier_name='code'):
        self.openbis = openbis_obj
        self.entity = entity
        self.df = df
        self.identifier_name = identifier_name

    def __repr__(self):
        return tabulate(self.df, headers=list(self.df))

    def __len__(self):
        return len(self.df)

    def _repr_html_(self):
        return self.df._repr_html_()

    def get_parents(self, **kwargs):
        if self.entity not in ['sample', 'dataset']:
            raise ValueError("{}s do not have parents".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                # get all objects that have this object as a child == parent
                try:
                    parents = getattr(self.openbis, 'get_' + self.entity.lower() + 's')(withChildren=ident, **kwargs)
                    dfs.append(parents.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, self.entity, pd.concat(dfs), self.identifier_name)
            else:
                return Things(self.openbis, self.entity, DataFrame(), self.identifier_name)

    def get_children(self, **kwargs):
        if self.entity not in ['sample', 'dataset']:
            raise ValueError("{}s do not have children".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                # get all objects that have this object as a child == parent
                try:
                    parents = getattr(self.openbis, 'get_' + self.entity.lower() + 's')(withParent=ident, **kwargs)
                    dfs.append(parents.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, self.entity, pd.concat(dfs), self.identifier_name)
            else:
                return Things(self.openbis, self.entity, DataFrame(), self.identifier_name)

    def get_samples(self, **kwargs):
        if self.entity not in ['space', 'project', 'experiment']:
            raise ValueError("{}s do not have samples".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                args = {}
                args[self.entity.lower()] = ident
                try:
                    samples = self.openbis.get_samples(**args, **kwargs)
                    dfs.append(samples.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, 'sample', pd.concat(dfs), 'identifier')
            else:
                return Things(self.openbis, 'sample', DataFrame(), 'identifier')

    get_objects = get_samples # Alias

    def get_datasets(self, **kwargs):
        if self.entity not in ['sample', 'experiment']:
            raise ValueError("{}s do not have datasets".format(self.entity))

        if self.df is not None and len(self.df) > 0:
            dfs = []
            for ident in self.df[self.identifier_name]:
                args = {}
                args[self.entity.lower()] = ident
                try:
                    datasets = self.openbis.get_datasets(**args, **kwargs)
                    dfs.append(datasets.df)
                except ValueError:
                    pass

            if len(dfs) > 0:
                return Things(self.openbis, 'dataset', pd.concat(dfs), 'permId')
            else:
                return Things(self.openbis, 'dataset', DataFrame(), 'permId')

    def __getitem__(self, key):
        if self.df is not None and len(self.df) > 0:
            row = None
            if isinstance(key, int):
                # get thing by rowid
                row = self.df.loc[[key]]
            elif isinstance(key, list):
                # treat it as a normal dataframe
                return self.df[key]
            else:
                # get thing by code
                row = self.df[self.df[self.identifier_name] == key.upper()]

            if row is not None:
                # invoke the openbis.get_<entity>() method
                return getattr(self.openbis, 'get_' + self.entity)(row[self.identifier_name].values[0])

    def __iter__(self):
        for item in self.df[[self.identifier_name]][self.identifier_name].iteritems():
            yield getattr(self.openbis, 'get_' + self.entity)(item[1])

            # return self.df[[self.identifier_name]].to_dict()[self.identifier_name]

