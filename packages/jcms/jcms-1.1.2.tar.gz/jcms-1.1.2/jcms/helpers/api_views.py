from rest_framework import viewsets, serializers
from rest_framework.exceptions import MethodNotAllowed


# Creates a standard serializer for a model
def create_serializer(api_model, serialize_fields):
    class ModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = api_model
            fields = serialize_fields

    return ModelSerializer


def get_model_set(main):
    class ObjectModelSet(viewsets.ModelViewSet):
        queryset = main.model.objects.all()
        lookup_field = main.lookup_field

        serializer_classes = {
            'list': main.overview_fields,
            'create': main.create_fields,
            'retrieve': main.retrieve_fields,
            'update': main.update_fields,
            'partial_update': main.update_fields,
            'destroy': main.delete_fields,
        }

        def list(self, request, *args, **kwargs):
            if main.overview or main.all:
                return super(ObjectModelSet, self).list(request, args, kwargs)
            raise MethodNotAllowed('Overview or all is not turned on')

        def create(self, request, *args, **kwargs):
            if main.create or main.all:
                return super(ObjectModelSet, self).create(request, *args, **kwargs)
            raise MethodNotAllowed('Create or all is not turned on')

        def retrieve(self, request, *args, **kwargs):
            if main.retrieve or main.all:
                return super(ObjectModelSet, self).retrieve(request, *args, **kwargs)
            raise MethodNotAllowed('Retrieve or all is not turned on')

        def update(self, request, *args, **kwargs):
            if main.update or main.all:
                return super(ObjectModelSet, self).update(request, *args, **kwargs)
            raise MethodNotAllowed('Update or all is not turned on')

        def partial_update(self, request, *args, **kwargs):
            if main.update or main.all:
                return super(ObjectModelSet, self).partial_update(request, *args, **kwargs)
            raise MethodNotAllowed('Update or all is not turned on')

        def destroy(self, request, *args, **kwargs):
            if main.delete or main.all:
                return super(ObjectModelSet, self).destroy(request, *args, **kwargs)
            raise MethodNotAllowed('Destroy or all is not turned on')

        def get_serializer_class(self):
            try:
                if self.serializer_classes[self.action] is not None:
                    return create_serializer(main.model, self.serializer_classes[self.action])

                raise KeyError
            except (KeyError, AttributeError):
                return create_serializer(main.model, main.basis_fields)

    return ObjectModelSet
