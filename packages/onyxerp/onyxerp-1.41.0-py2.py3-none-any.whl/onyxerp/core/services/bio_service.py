from collections import OrderedDict

from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class BioService(Request, OnyxErpService):
    """
    Serviço responsável pela interação de APIs do OnyxERP com a BiometriaAPI
    """
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(BioService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "SocialAPI")

    def inserir_bio(self):
        """
        Cadastra os registros biométricos de digital de uma pessoa física na BiometriaAPI
        """
        response = self.post("/v2/bio/")

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def search_by_face(self) -> OrderedDict or False:
        """
        Envia uma pesquisa por biometria facial à BioAPI.
        :return: bool
        """
        request = self.search_by_face_verbose()

        if type(request) is OrderedDict:
            return request
        else:
            return False

    def search_by_face_verbose(self) -> OrderedDict or int:
        """
        Envia uma pesquisa por biometria facial à BioAPI e retorna o status-code recebido no POST.
        :return: OrderedDict or int
        """
        request = self.post("/v1/face-id/search/")

        status = request.get_status_code()

        if status == 200:
            response = request.get_decoded()
            return response['data']['BiometriaAPI']
        else:
            return status
