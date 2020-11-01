from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from urllib.parse import urljoin


class GoogleCloudStaticFileStorage(GoogleCloudStorage):

    bucket_name =setting('GS_STATIC_BUCKET_NAME')

    def  url(self, name):
        return urljoin(settings.STATIC_URL, name)