from datetime import datetime
from collections import OrderedDict

from django.http.request import HttpRequest
from django.utils.http import urlsafe_base64_decode
from rinzler.exceptions.auth_exception import AuthException
from onyxerp.core.services.app_service import AppService
import jwt
import base64
import json


class JwtService(object):

    """
    JwtService
    """
    app_service = object
    __jwt_alg = "HS256"
    __cleared_routes = dict()
    __config = dict()
    __exp_secs = 43200

    def __init__(self, config: dict(), app: object()):
        self.__config = config
        self.app_service = AppService(config, app)
        self.__cleared_routes = config["JWT_ROUTES_WHITE_LIST"]

    def authenticate(self, request: HttpRequest, auth_route: str(), params: dict()):
        """

        :param request:
        :param auth_route:
        :param params:
        :return:
        """
        if auth_route not in self.__cleared_routes:

            token = self.get_authorization_jwt(request)
            data = self.check_jwt(token, auth_route)

            return {
                "token": token,
                "data": data,
            }
        else:
            return dict()

    def get_authorization_jwt(self, request: HttpRequest):
        """

        :param request:
        :return:
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthException("JWT não informado.")

        token = request.META['HTTP_AUTHORIZATION']
        if 'Bearer ' not in token:
            raise AuthException("JWT não informado.")
        return token[7:]

    def encode(self, dados: dict()):
        """

        :param dados:
        :return:
        """
        try:
            app_key = base64.encodebytes(dados['app']['apikey'].encode("utf-8"))

            dados_app = self.app_service.get_app(app_key.decode("utf-8"))
            key = base64.b64encode(dados_app['data']['apiSecret'].encode('utf-8'))

            iat = int(datetime.now().timestamp())

            dados_jwt = OrderedDict()
            dados_jwt['iat'] = iat
            dados_jwt['iss'] = "Onyxprev"
            dados_jwt['exp'] = iat + self.__exp_secs
            dados_jwt['nbf'] = iat
            dados_jwt['data'] = dados

            return jwt.encode(dados_jwt, key).decode('utf-8')
        except BaseException as e:
            raise AuthException("Token inválido ou expirado.")

    def decode(self, token, key):
        """

        :param token:
        :param key:
        :return:
        """
        try:
            return jwt.decode(token, key)
        except BaseException as e:
            raise AuthException("Token inválido ou expirado.")

    def get_jwt_payload(self, token):
        """

        :param token:
        :return:
        """
        exp = token.split(".")
        payload = urlsafe_base64_decode(exp[1])
        return json.loads(payload.decode("utf-8"))

    def check_jwt(self, token: str(), auth_route: str()):
        """

        :param token:
        :param auth_route:
        :return:
        """
        try:
            exp = token.split(".")
            payload = urlsafe_base64_decode(exp[1])
            json_data = json.loads(payload.decode("utf-8"))

            app_key = base64.encodebytes(json_data['data']['app']['apikey'].encode("utf-8"))

            app_data = self.app_service.get_app(app_key.decode("utf-8"))
            key = base64.b64encode(app_data['data']['apiSecret'].encode("utf-8"))
            return self.decode(token, key)
        except Exception as e:
            raise AuthException("Token inválido ou expirado.")

    def build_fake_jwt(self, app_id: str, dados_user: dict) -> dict:
        """
        Constrói um JWT Fake, porém válido, para interação entre as APIs.
        :param app_id: str Id da aplicação que assina o token, normalmente CONFIG["APP_ID"]
        :param dados_user: dict Dict contendo a estrtutura minima:
            {
                'oid': "(Id do órgão)"
                'oeid': "(Id da entidade)"
                'pfid': "(pf_id do usuário)"
            }
        :return: dict
        """
        dados = {
            'app': {
                'apikey': app_id,
                'apiId': app_id,
            },
            'user': dados_user
        }
        token = self.encode(dados)
        return {
            'token': token,
            'data': self.get_jwt_payload(token)
        }
