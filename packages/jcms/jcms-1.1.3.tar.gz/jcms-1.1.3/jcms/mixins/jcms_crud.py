from django.urls import path
from abc import ABCMeta
from jcms.helpers.crud_views import list_view, detail_view, create_view, edit_view, delete_view


# Creates all views needed for a model
class JcmsCrud(object):
    __metaclass__ = ABCMeta

    def __init__(self, model, create_edit_list, list_fields=[], icon=''):
        self.model = model
        self.create_edit_list = create_edit_list
        self.list_fields = list_fields if list_fields else create_edit_list
        self.icon = icon
        self.model_name = model.__name__.lower()

    # Gets all url objects for to create the urls
    def get_urls(self):
        return [
            path(self.model_name + '/', self.list_view(), name=self.model_name + 'List'),
            path(self.model_name + '/<int:pk>/', self.detail_view(), name=self.model_name + 'Detail'),
            path(self.model_name + '/create/', self.create_view(), name=self.model_name + 'Create'),
            path(self.model_name + '/<int:pk>/delete/', self.delete_view(), name=self.model_name + 'Delete'),
            path(self.model_name + '/<int:pk>/edit/', self.edit_view(), name=self.model_name + 'Edit'),
        ]

    # So it can be overwritten
    def list_view(self):
        return list_view(self)

    # So it can be overwritten
    def detail_view(self):
        return detail_view(self)

    # So it can be overwritten
    def create_view(self):
        return create_view(self)

    # So it can be overwritten
    def edit_view(self):
        return edit_view(self)

    # So it can be overwritten
    def delete_view(self):
        return delete_view(self)


