from sanic import Blueprint
from sanic.response import json
from sanic import response
from sanic_jwt import protected
from longitude import config
from longitude.exceptions import abort, NotFound


from .model import CredentialModel, CredentialSchema

bp = Blueprint('longitude.credentials', url_prefix='/credentials')


@bp.get('/')
@protected()
async def list_credentials(request):
    m = CredentialModel(request.app.sql_model)
    return json(await m.list())


@bp.get('/types')
async def list_credential_types(request):
    return json(config.CREDENTIALS_TYPES)


@bp.get('/<oid:int>')
@protected()
async def credentials(request, oid):
    m = CredentialModel(request.app.sql_model)
    return json(await m.get(oid))


@bp.post('/')
@protected()
async def credentials(request):
    data, errors = CredentialSchema().load(request.json)

    if errors:
        return json(errors, 400)

    m = CredentialModel(request.app.sql_model)
    return json(await m.upsert(data))


@bp.put('/<oid:int>')
@protected()
async def credentials(request, oid):
    data, errors = CredentialSchema().load(request.json)

    if errors:
        return json(errors, 400)

    data['id'] = oid

    m = CredentialModel(request.app.sql_model)
    return json(await m.upsert(data))


@bp.delete('/<oid:int>')
@protected()
async def credentials(request, oid):
    m = CredentialModel(request.app.sql_model)
    return json(await m.delete(oid))
