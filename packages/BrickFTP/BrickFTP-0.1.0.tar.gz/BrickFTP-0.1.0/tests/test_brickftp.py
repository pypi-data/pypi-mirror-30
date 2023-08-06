from pathlib import Path
import os

import pytest

from brickftp import BrickFTP, BrickFTPError

BRICK_FTP_USER = os.environ['BRICK_FTP_USER']
BRICK_FTP_PASS = os.environ['BRICK_FTP_PASS']
BRICK_FTP_SUBDOMAIN = os.environ['BRICK_FTP_SUBDOMAIN']


@pytest.fixture
def client():
    client = BrickFTP(
        username=BRICK_FTP_USER,
        password=BRICK_FTP_PASS,
        subdomain=BRICK_FTP_SUBDOMAIN,
    )
    yield client
    names = (i['display_name'] for i in client.dir('/'))
    for path in names:
        client.delete(path)


def test_login(client):
    assert client._session_id is None

    client._login()

    assert client._session_id is not None
    assert client._logged_in is True


def test_login_with_invalid_creds():
    client = BrickFTP(
        username='aaa',
        password='aaa',
        subdomain='aaa',
    )
    with pytest.raises(BrickFTPError):
        client._login()


def test_folders(client, mocker):
    client.upload(
        upload_path='data.txt',
        local_path=Path(Path(__file__).parent, 'data.txt'),
    )

    resp_json = client.dir('/')

    assert len(resp_json) > 0
    for item in resp_json:
        exp_item_keys = (
            'crc32', 'display_name', 'id', 'md5', 'mtime', 'path',
            'permissions', 'provided_mtime', 'size', 'type'
        )
        assert isinstance(item, dict)
        assert set(exp_item_keys).issubset(item.keys())


def test_upload(client):
    client.upload(
        upload_path='data.txt',
        local_path=Path(Path(__file__).parent, 'data.txt'),
    )

    resp_json = client.dir('/')
    assert 'data.txt' in [i['path'] for i in resp_json]


def test_download(client):
    client.upload(
        upload_path='data2.txt',
        local_path=Path(Path(__file__).parent, 'data.txt'),
    )

    client.download_file(remote_path='data2.txt', local_path='/tmp/data2.txt'),

    assert os.path.isfile('/tmp/data2.txt')


def test_delete(client):
    client.upload(
        upload_path='data.txt',
        local_path=Path(Path(__file__).parent, 'data.txt'),
    )

    client.delete('data.txt')

    assert len(client.dir('/')) == 0
