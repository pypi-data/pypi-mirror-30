from jcms.helpers.api_views import get_model_set
from rest_framework import routers


class JcmsApi:
    def __init__(
        self, model,
        basis_fields,
        lookup_field='pk',
        create=False, create_fields=None,
        retrieve=False, retrieve_fields=None,
        update=False, update_fields=None,
        delete=False, delete_fields=None,
        overview=False, overview_fields=None,
        all=False
    ):

        self.model = model
        self.basis_fields = basis_fields
        self.lookup_field = lookup_field

        # Crud variables
        self.create = create
        self.create_fields = create_fields

        self.retrieve = retrieve
        self.retrieve_fields = retrieve_fields

        self.update = update
        self.update_fields = update_fields

        self.delete = delete
        self.delete_fields = delete_fields

        self.overview = overview
        self.overview_fields = overview_fields

        self.all = all

        # Variables that are used very often
        self.model_name = model.__name__.lower()

    # makes the urls
    def get_urls(self):
        view = get_model_set(self)
        router = routers.SimpleRouter()
        router.register(r'api/' + self.model_name, view)

        return router.urls
