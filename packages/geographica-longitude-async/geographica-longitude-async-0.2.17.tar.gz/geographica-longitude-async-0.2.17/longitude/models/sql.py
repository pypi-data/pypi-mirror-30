import itertools
import pgpy

from sanic.log import logger
from longitude.utils import is_list_or_tuple
from longitude import config
from longitude.exceptions import NotFound


class SQLFetchable:
    def fetch(self, *args, **kwargs):
        raise RuntimeError('not implemented')


class SQLCRUDModel:

    table_name = None
    encoded_columns = tuple()
    select_columns = ('*',)

    def __init__(self, db_model: SQLFetchable):
        self.db_model = db_model

    async def list(self, **filters):
        sql, params = self.placeholder_to_ordinal(*self.select_sql(**filters))

        ret = await self._fetch(sql, *params)
        return {
            'results': ret
        }

    async def get(self, oid=None, **filters):

        if oid is not None:
            filters['oid'] = oid

        ret = (await self.list(**filters))['results']

        if len(ret) == 1:
            return ret[0]
        elif len(ret) == 0:
            raise NotFound('Object not found')
        else:
            raise AssertionError(
                'SQLCRUDModel.get can only return 0 or 1 '
                'elements.'
            )

    async def upsert(self, values, pk=('id',), returning_columns=None):

        params = {}

        values = self.patch_insert_columns_encoded(values)
        values = self.patch_insert_columns(values)

        if returning_columns is None:
            returning_columns = self.select_columns

        insert_columns_snippet = []
        conflict_snippet = []
        values_snippet = []

        for key, val in values.items():

            if is_list_or_tuple(val, length=2):
                val, right_side_tpl = val
            else:
                right_side_tpl = '${}'

            param_name = self.add_param_name(key, val, params)
            insert_columns_snippet.append(key)
            conflict_snippet.append(('{}=' + right_side_tpl).format(key, param_name))
            values_snippet.append(right_side_tpl.format(param_name))

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

    async def delete(self, oid=None, **filters):

        if oid is not None:
            filters['oid'] = oid

        sql, params = self.placeholder_to_ordinal(*self.delete_sql(**filters))

        ret = await self._fetch(sql, *params)

        if len(ret) == 0:
            raise NotFound('Object not found')

        return {
            'results': ret
        }

    def select_sql(self, params=None, columns=None, **filters):

        if columns is None:
            columns = self.select_columns

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

    def delete_sql(self, params=None, **filters):

        if params is None:
            params = {}

        where_clause, params = self.where_sql(params, **filters)

        return (
            '''
                DELETE FROM {schema}{table}
                WHERE {where_clause}
                RETURNING id
            '''.format(
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause
            ),
            params
        )

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
        ret = await self.db_model.fetch(*args, **kwargs)
        ret = self.decode_objects(ret)
        return ret

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
            if ('$' + named_param) in sql:
                sql = sql.replace('$' + named_param, '$' + str(ordinal))
                ordinal_params.append(params[named_param])

        return sql, ordinal_params

    def patch_insert_columns_encoded(self, data):
        for attr_name in self.encoded_columns:
            if attr_name in data and not is_list_or_tuple(data[attr_name], length=2):
                data[attr_name] = (data[attr_name], 'pgp_pub_encrypt(${}, dearmor(get_pgp_pubkey()))')

        return data

    def patch_insert_columns(self, values):

        values.pop('created_at', None)

        if 'updated_at' in self.select_columns:
            values['updated_at'] = ('', 'CURRENT_TIMESTAMP')

        return values

    def decode_objects(self, data):

        if not config.PGP_PRIVATE_KEY:
            return data

        is_single = isinstance(data, dict)

        if is_single:
            data = [data]

        for obj in data:
            for encoded_attr in set(self.encoded_columns).intersection(obj.keys()):
                if obj[encoded_attr] is not None:
                    try:
                        db_crypted_attr = pgpy.PGPMessage.from_blob(obj[encoded_attr])
                        obj[encoded_attr] = config.PGP_PRIVATE_KEY[0].decrypt(db_crypted_attr).message
                    except ValueError as e:
                        obj[encoded_attr] = None
                        logger.warning(
                            "Couldn't decode attribute attribute %s of object with %s.%s: %s",
                            encoded_attr,
                            self.__class__.__name__,
                            str(obj.get('id', 'UNKNOWN')),
                            str(e)
                        )

        if is_single:
            data = data[0]

        return data
