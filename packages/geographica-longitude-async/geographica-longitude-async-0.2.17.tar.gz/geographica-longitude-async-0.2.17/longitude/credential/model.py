from marshmallow import Schema, fields
from longitude.models.sql import SQLCRUDModel
from longitude.validators import max_length, not_blank, combine_validations, choices_in
from longitude import config


class CredentialSchema(Schema):

    active = fields.Boolean()

    type = fields.String(
        validate=combine_validations(
            max_length(32),
            not_blank,
            choices_in(config.CREDENTIALS_TYPES)
        ),
        required=True
    )

    auth_name = fields.String()
    key = fields.String(required=True)
    expires = fields.DateTime() # default iso8601


class CredentialModel(SQLCRUDModel):
    table_name = 'longitude_credentials'

    encoded_columns = (
        'auth_name',
        'key'
    )

    select_columns = (
        "id",
        "active",
        "type",
        "auth_name",
        "created_at",
        "updated_at",
        "expires"
    )


