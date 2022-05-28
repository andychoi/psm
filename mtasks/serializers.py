from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from common.serializers import CBUSerializer
from users.models import Profile
from .models import Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'username',
            # 'first_name',
            # 'last_name',
        )


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    CBU = CBUSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'number',
            'title',
            'CBU',
            'user',
            'description',
            'resolution',
            'deadline',
            'state',
            'created_at',
        )


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
