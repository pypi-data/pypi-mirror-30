from directory_cms_client.base import BaseAPIClient


class FindASupplierClient(BaseAPIClient):

    page_types = {
        'industry': 'find_a_supplier.IndustryPage',
        'industries-landing-page': 'find_a_supplier.IndustryLandingPage',
    }

    def list_industry_pages(self, *args, **kwargs):
        return self.list_pages(
            page_type=self.page_types['industry'],
            fields='hero_image,title,url',
            *args,
            **kwargs
        )

    def get_industries_landing_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['industries-landing-page'],
            *args,
            **kwargs
        )
