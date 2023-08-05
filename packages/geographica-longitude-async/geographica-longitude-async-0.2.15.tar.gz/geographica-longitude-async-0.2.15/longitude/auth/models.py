from longitude.models.sql import SQLCRUDModel


class UserModel(SQLCRUDModel):
    table_name = 'auth_user'

    def where_sql(self, params, username=None, password=None, **filters):
        where_clause, params = super().where_sql(params, **filters)

        if username is not None:
            name = self.add_param_name('username', username, params)
            where_clause += ' AND username=${}'.format(name)

        if password is not None:
            name = self.add_param_name('password', password, params)
            where_clause += ' AND password=${}'.format(name)

        return where_clause, params
