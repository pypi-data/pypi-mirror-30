from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q


def base_view_class(crud):
    class BaseViewClass(LoginRequiredMixin, PermissionRequiredMixin):
        model = crud.model
        permission_required = 'jcms.create_' + crud.model_name

    return BaseViewClass


def create_edit_class(crud):
    class CreateEditClass(base_view_class(crud)):
        fields = crud.create_edit_list
        template_name = 'jcms-admin/crud/edit_or_create.html'
        success_url = reverse_lazy('jcms:' + crud.model_name + 'List')

    return CreateEditClass


# List view with permission create_model_name
def list_view(crud):
    class ObjectList(base_view_class(crud), ListView):
        fields = crud.list_fields
        template_name = 'jcms-admin/crud/list.html'

        def get_queryset(self):
            query_set = get_search_queryset(self)
            if query_set:
                return query_set

            return super(ObjectList, self).get_queryset()

    return ObjectList.as_view()


# Detail view with permission create_model_name
def detail_view(crud):
    class ObjectDetail(base_view_class(crud), DetailView):
        template_name = 'jcms-admin/crud/detail.html'

    return ObjectDetail.as_view()


# Create view with permission create_model_name
def create_view(crud):
    class ObjectCreate(create_edit_class(crud), SuccessMessageMixin, CreateView):
        success_message = 'Successfully created ' + crud.model_name

    return ObjectCreate.as_view()


# Edit view with permission change_model_name
def edit_view(crud):
    class ObjectEdit(create_edit_class(crud), SuccessMessageMixin, UpdateView):
        permission_required = 'jcms.change_' + crud.model_name
        success_message = 'Successfully edited ' + crud.model_name

    return ObjectEdit.as_view()


# Delete view with permission delete_model_name
def delete_view(crud):
    class ObjectDelete(base_view_class(crud), DeleteView):
        permission_required = 'jcms.delete_' + crud.model_name
        success_url = reverse_lazy('jcms:' + crud.model_name + 'List')
        success_message = 'Successfully deleted ' + crud.model_name

        def delete(self, request, *args, **kwargs):
            messages.success(self.request, self.success_message)
            return super(ObjectDelete, self).delete(request, *args, **kwargs)

    return ObjectDelete.as_view()


def get_search_queryset(crud):
    search_term = crud.request.GET.get('search')
    if search_term:
        print(search_term)
        queries = [Q(**{f + '__icontains': search_term}) for f in crud.fields]
        qs = Q()
        for query in queries:
            qs = qs | query

        return crud.model.objects.filter(qs)

    return None
