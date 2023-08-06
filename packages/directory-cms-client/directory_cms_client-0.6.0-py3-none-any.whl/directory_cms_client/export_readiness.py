from directory_cms_client.base import BaseAPIClient


class ExportReadinessClient(BaseAPIClient):

    page_types = {
        'terms-and-conditions': 'export_readiness.TermsAndConditionsPage',
    }

    def get_terms_and_conditions_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['terms-and-conditions'],
            *args,
            **kwargs
        )
