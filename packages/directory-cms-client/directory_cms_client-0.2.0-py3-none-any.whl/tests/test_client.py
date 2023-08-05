import requests_mock

from directory_cms_client import DirectoryCMSClient


def test_cms_client_draft():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock() as mock:
        mock.get('http://example.com/api/pages/1/')
        client.get_page(1, draft_token='123')
        request = mock.request_history[0]

    assert request.qs == {'draft_token': ['123']}


def test_cms_client_language():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock() as mock:
        mock.get('http://example.com/api/pages/1/')
        client.get_page(1, language_code='de')
        request = mock.request_history[0]

    assert request.qs == {'lang': ['de']}


def test_cms_client_published():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock() as mock:
        mock.get('http://example.com/api/pages/2/')
        client.get_page(2)
        request = mock.request_history[0]

    assert request.qs == {}


def test_cms_client_pages():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_pages('thing')
        request = mock.request_history[0]

    assert request.qs == {
        'type': ['thing'],
        'fields': ['*']
    }
