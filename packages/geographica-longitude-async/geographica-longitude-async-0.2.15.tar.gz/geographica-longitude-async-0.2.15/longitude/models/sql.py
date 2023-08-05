import itertools
from longitude import config


class SQLFetchable:
    def fetch(self, *args, **kwargs):
        raise RuntimeError('not implemented')


class SQLCRUDModel:

    table_name = None

    def __init__(self, db_model: SQLFetchable):
        self.db_model = db_model

    async def list(self, **filters):
        sql, params = self.placeholder_to_ordinal(*self.select_sql(**filters))

        ret = await self._fetch(sql, *params)
        return ret

    async def get(self, oid, **filters):
        filters['oid']=oid

        ret = await self.list(**filters)

        if len(ret)==1:
            return ret[0]
        elif len(ret)==0:
            return None
        else:
            raise AssertionError(
                'SQLCRUDModel.get can only return 0 or 1 '
                'elements.'
            )

    def select_sql(self, params=None, columns=tuple('*'), **filters):

        if params is None:
            params = {}

        where_clause, params = self.where_sql(params, **filters)

        return (
            '''
                SELECT 
                    {columns}
                FROM {schema}{table}
                WHERE {where_clause}
            '''.format(
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause,
                columns=','.join(columns)
            ),
            params
        )

    def where_sql(self, params, **filters):

        oid = filters.get('oid', None)

        if oid:
            name = self.add_param_name('id', oid, params)

            snippet = '{schema}{table}=${name}'.format(
                schema=self.schema,
                table=self.table_name,
                name=name
            )
        else:
            snippet = 'TRUE'

        return snippet, params

    async def _fetch(self, *args, **kwargs):
        return await self.db_model.fetch(*args, **kwargs)

    @property
    def schema(self):
        return config.DB_SCHEMA + '.' if config.DB_SCHEMA \
            else ''

    @staticmethod
    def add_param_name(name, value, params):

        if name in params:
            for i in itertools.count(1):
                name = name + str(i)
                if name not in params:
                    break

        params[name] = value

        return name

    @staticmethod
    def placeholder_to_ordinal(sql, params):
        ordinal_params = []
        for ordinal, named_param in zip(itertools.count(1), params.keys()):
            sql = sql.replace('$' + named_param, '$' + str(ordinal))
            ordinal_params.append(params[named_param])

        return sql, ordinal_params
