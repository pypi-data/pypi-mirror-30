import hashlib
import logging
import os
import urllib.parse

import aiohttp


logger = logging.getLogger(__name__)

class Backblaze:

    API_NAME = 'b2api/'
    API_VERSION = 'v1/'
    API_DOMAIN = 'https://api.backblazeb2.com'
    API_ENDPOINTS = {
        'list_buckets': 'b2_list_buckets/',
        'get_upload_url': 'b2_get_upload_url/',
        'authorize_account': 'b2_authorize_account/',
    }

    def __init__(self, account_id=None, app_key=None):
        self._account_id = account_id
        self._app_key = app_key
        self._authorized_base_url = None
        self._authorization_token = None
        self._authorized_session = None

    def _create_url(self, api_endpoint):
        path = '{}{}{}'.format(self.API_NAME, self.API_VERSION,
                               self.API_ENDPOINTS[api_endpoint])
        if self._authorized_base_url is None:
            return urllib.parse.urljoin(self.API_DOMAIN, path)
        else:
            return urllib.parse.urljoin(self._authorized_base_url, path)

    async def authenticate(self):
        url = self._create_url('authorize_account')
        auth = aiohttp.BasicAuth(self._account_id, self._app_key)
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                response_js = await response.json()
                self._authorized_base_url = response_js.get('apiUrl')
                self._authorization_token = response_js.get(
                    'authorizationToken')
                self._authorized_session = aiohttp.ClientSession(
                    headers={'Authorization': self._authorization_token})
                return response_js

    async def _get_upload_url(self, bucket_id):
        url = self._create_url('get_upload_url')
        async with self._authorized_session as session:
            async with session.post(
                    url, json={'bucketId': bucket_id}) as response:
                response.raise_for_status()
                response_js = await response.json()
                return response_js

    async def upload_file(self, bucket_id, file_to_upload, content_type):
        try:
            upload_details = await self._get_upload_url(bucket_id)
        except aiohttp.ClientResponseError:
            logger.exception('Unable to upload file')
        else:
            upload_url = upload_details.get('uploadUrl')
            upload_token = upload_details.get('authorizationToken')
            with open(file_to_upload, 'rb') as f:
                file_data = f.read()
            upload_headers = {
                'Authorization': upload_token,
                'X-Bz-File-Name': urllib.parse.quote(
                    os.path.basename(file_to_upload)),
                'Content-Type': content_type,
                'X-Bz-Content-Sha1': hashlib.sha1(file_data).hexdigest()
            }
            async with aiohttp.ClientSession(
                    headers=upload_headers) as session:
                async with session.post(upload_url, data=file_data) as response:
                    response.raise_for_status()
                    response_js = await response.json()
                    return response_js
