import requests_mock

from directory_cms_client.find_a_supplier import FindASupplierClient


def test_list_industry_pages():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_industry_pages()
        request = mock.request_history[0]

    assert request.qs == {
        'type': [FindASupplierClient.page_types['industry']],
        'fields': ['hero_image,title,url'],
    }


def test_list_industry_pages_language_code():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_industry_pages(language_code='de')
        request = mock.request_history[0]

    assert request.qs == {
        'type': [FindASupplierClient.page_types['industry']],
        'fields': ['hero_image,title,url'],
        'lang': ['de']
    }


def test_list_industry_pages_draft_token():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_industry_pages(draft_token='thing')
        request = mock.request_history[0]

    assert request.qs == {
        'type': [FindASupplierClient.page_types['industry']],
        'fields': ['hero_image,title,url'],
        'draft_token': ['thing']
    }


def test_get_industries_landing_page_language():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industries-landing-page']
        ))
        client.get_industries_landing_page(language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_get_industries_landing_page_draft():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industries-landing-page']
        ))
        client.get_industries_landing_page(draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }
