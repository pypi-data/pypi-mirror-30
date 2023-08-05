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

    async def get(self, oid=None, **filters):

        if oid is not None:
            filters['oid'] = oid

        ret = await self.list(**filters)

        if len(ret) == 1:
            return ret[0]
        elif len(ret) == 0:
            return None
        else:
            raise AssertionError(
                'SQLCRUDModel.get can only return 0 or 1 '
                'elements.'
            )

    async def upsert(self, values, pk=('id',), returning_columns=None):

        params = {}

        if returning_columns is None:
            returning_columns = self.default_select_columns()

        insert_columns_snippet = []
        conflict_snippet = []
        values_snippet = []

        for key, val in values.items():
            param_name = self.add_param_name(key, val, params)
            insert_columns_snippet.append(key)
            values_snippet.append('$' + param_name)
            conflict_snippet.append('{}=${}'.format(key, param_name))

        sql = '''
            INSERT INTO {schema}{table} (
              {columns}
            ) VALUES (
              {values}
            )
            ON CONFLICT ({keys}) DO UPDATE SET
              {conflict}
            RETURNING {returning_columns}
        '''.format(
            schema=self.schema,
            table=self.table_name,
            columns=','.join(insert_columns_snippet),
            values=','.join(values_snippet),
            keys=','.join(pk),
            conflict=','.join(conflict_snippet),
            returning_columns=','.join(returning_columns)
        )

        sql, params = self.placeholder_to_ordinal(sql, params)

        ret = await self._fetch(sql, *params)

        return ret[0]

    def select_sql(self, params=None, columns=None, **filters):

        if columns is None:
            columns = self.default_select_columns()

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

    def default_select_columns(self):
        return tuple('*')

    def where_sql(self, params, **filters):

        oid = filters.get('oid', None)

        if oid:
            name = self.add_param_name('id', oid, params)

            snippet = '{schema}{table}.id=${name}'.format(
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
