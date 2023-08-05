import boto3
from botocore.config import Config


class S3Service(object):
    """
    S3Service
    """
    app = object
    s3_bucket_name = str
    s3_client = object

    def __init__(self, app: object, s3_bucket_name: str, s3_credentials: dict):
        self.app = app
        self.s3_bucket_name = s3_bucket_name
        self.s3_client = self.get_s3_client(s3_credentials)

    def put_file_to_s3(self, file_id: str, data: bytes, acl='public-read') -> bool:
        """
        Envia um arquivo para o S3
        :param file_id: str
        :param data: bytes Bytes do arquivo
        :param acl: str Política de acesso ao arquivo na AWS
        :return: bool
        """
        try:
            self.s3_client.Bucket(self.s3_bucket_name).put_object(Key=file_id, ACL=acl, Body=data)
            self.app['log'].info("Arquivo %s salvo no S3 com sucesso." % file_id)
            return True
        except Exception:
            self.app['log'].error(
                'O file_id %s informado não pôde ser salvo no Bucket %s no S3' % (file_id, self.s3_bucket_name),
                exc_info=True
            )
            return False

    def get_file_from_s3(self, file_id: str) -> bytes or False:
        """
        Recupera os bytes de um arquivo do S3
        :param file_id: str
        :return: bytes or False
        """
        try:
            obj = self.s3_client.Object(self.s3_bucket_name, file_id)
            self.app['log'].info("Arquivo %s recuperado do S3 com sucesso." % file_id)
            data = obj.get()['Body'].read()
            return data
        except Exception:
            self.app['log'].error(
                'O file_id %s informado não pôde ser localizado no Bucket %s no S3' % (file_id, self.s3_bucket_name),
                exc_info=True
            )
            return False

    @staticmethod
    def get_s3_client(s3_credentials: dict):
        """
        Monta um S3 Client's object
        :return: object
        """
        return boto3.resource(
            's3',
            aws_access_key_id=s3_credentials['aws_access_key_id'],
            aws_secret_access_key=s3_credentials['aws_secret_access_key'],
            config=Config(signature_version='s3v4')
        )
