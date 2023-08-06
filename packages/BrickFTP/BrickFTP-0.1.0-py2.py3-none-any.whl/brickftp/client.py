import logging

import requests

logger = logging.getLogger(__name__)


class BrickFTPError(Exception):
    pass


class BrickFTP:

    def __init__(self, *, username, password, subdomain):
        self._username = username
        self._password = password
        self._subdomain = subdomain
        self._session_id = None
        self._logged_in = False

    def _login(self):
        start_session_resp = self._post(
            '/api/rest/v1/sessions.json',
            json={'username': self._username, 'password': self._password}
        )
        self._session_id = start_session_resp['id']
        self._logged_in = True
        self._get('/api/rest/v1/users.json')

    def dir(self, remote_path):
        if not self._logged_in:
            self._login()
        return self._get(f'/api/rest/v1/folders/{remote_path.lstrip("/")}')

    def upload(self, *, upload_path, local_path):
        # NOTE: can currently only upload upto 5MB size files
        # https://developers.brickftp.com/#requesting-additional-upload-urls
        if not self._logged_in:
            self._login()
        upload_path = upload_path.lstrip('/')
        upload_control_url = f'/api/rest/v1/files/{upload_path}'
        # Start upload
        start_upload_resp_json = self._post(
            upload_control_url,
            json={'action': 'put'},
        )
        # Upload parts
        ref = start_upload_resp_json['ref']
        upload_uri = start_upload_resp_json['upload_uri']
        with open(local_path) as input_file:
            resp = requests.put(upload_uri, data=input_file.read())
            if not resp.ok:
                raise BrickFTPError('Failed to upload part. Resp: {resp.text}')
        # End upload
        self._post(upload_control_url, json={'action': 'end', 'ref': ref})

    def download_file(self, *, remote_path, local_path):
        if not self._logged_in:
            self._login()
        remote_path = remote_path.lstrip('/')
        dl_info = self._get(
            f'/api/rest/v1/files/{remote_path}',
        )
        resp = requests.get(dl_info['download_uri'])
        resp.raise_for_status()
        file_bytes = resp.content
        with open(local_path, 'wb') as file_:
            file_.write(file_bytes)

    def delete(self, remote_path):
        if not self._logged_in:
            self._login()
        remote_path = remote_path.lstrip('/')
        self._delete(
            f'/api/rest/v1/files/{remote_path}', headers={'Depth': 'infinity'}
        )

    def _post(self, path, **kwargs):
        return self._request(path=path, method='post', **kwargs)

    def _get(self, path):
        return self._request(path=path, method='get')

    def _delete(self, path, **kwargs):
        return self._request(path=path, method='delete', **kwargs)

    def _request(self, *, path, method, **kwargs):
        url = (
            f'https://{self._subdomain}.brickftp.com/{path.lstrip("/")}'
        )
        resp = getattr(requests, method)(
            url, **{**self._default_request_kwargs, **kwargs}
        )
        resp_json = resp.json()
        if not resp.ok:
            error = resp_json['error']
            raise BrickFTPError(error)
        return resp_json

    @property
    def _default_request_kwargs(self):
        if self._logged_in:
            return {'cookies': {'BrickAPI': self._session_id}}
        elif not self._logged_in and self._session_id:
            return {'auth': (self._session_id, 'x')}
        else:
            return {}
