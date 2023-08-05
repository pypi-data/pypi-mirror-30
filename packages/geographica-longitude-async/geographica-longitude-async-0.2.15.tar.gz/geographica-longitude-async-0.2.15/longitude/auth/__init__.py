from sanic_jwt import Configuration as OriginalConfiguration, Initialize
from sanic.exceptions import InvalidUsage
from longitude import config
from sanic_jwt.exceptions import AuthenticationFailed
from longitude.auth.models import UserModel


class Configuration(OriginalConfiguration):
    pass


async def authenticate(request):

    if request.json is None:
        raise InvalidUsage("JSON payload required.")

    payload_invalid = not isinstance(request.json, dict) or \
                      len({'username', 'password'} & set(request.json.keys()))!=2

    if payload_invalid:
        raise InvalidUsage("JSON payload must include username and password.")

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    model = UserModel(request.app.sql_model)
    user = await model.list(username=username, password=password)

    if user is None:
        raise AuthenticationFailed("User not found or password incorrect.")

    return user


def init_jwt(app, *args, **kwargs):

    Initialize(
        app,
        authenticate=kwargs.get('authenticate', authenticate),
        access_token_name=config.SECRET_KEY,
        configuration_class=Configuration,
        *args,
        **kwargs
    )