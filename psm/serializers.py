from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from common.serializers import CBUSerializer
from users.models import Profile
from .models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    pass
    # CBU = CBUSerializer(read_only=True)
    # user = UserSerializer(read_only=True)

    # class Meta:
    #     model = Project
    #     fields = (
    #         'number',
    #         'title',
    #         'CBU',
    #         'user',
    #         'description',
    #         'resolution',
    #         'deadline',
    #         'state',
    #         'created_at',
    #     )


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
