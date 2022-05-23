from rest_framework import serializers, viewsets

from .models import CBU

#FIXME
# class CBUSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = CBU
#         fields = (
#             'name',
#         )


# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = CBU.objects.all()
#     serializer_class = CBUSerializer
