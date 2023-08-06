import requests_mock

from directory_cms_client.export_readiness import ExportReadinessClient


def test_get_terms_and_conditions_page_language():
    client = ExportReadinessClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            ExportReadinessClient.page_types['terms-and-conditions']
        ))
        client.get_terms_and_conditions_page(language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_get_terms_and_conditions_page_draft():
    client = ExportReadinessClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            ExportReadinessClient.page_types['terms-and-conditions']
        ))
        client.get_terms_and_conditions_page(draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }
