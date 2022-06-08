from rest_framework import serializers

from psm.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [ 'id', 'code', 'title', 'p_pre_plan_b', 'p_close', 'progress', 'CBU', 'priority' ]
