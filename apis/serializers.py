from rest_framework import serializers

from psm.models import Project
from users.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [ 'id', 'username', 'email']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        depth = 1
        fields = [ 'id', 'code', 'title'
            , 'p_ideation', 'p_plan_b', 'p_plan_e', 'p_kickoff', 'p_design_b', 'p_design_e', 'p_dev_b', 'p_dev_e', 'p_uat_b', 'p_uat_e', 'p_launch', 'p_close'
            , 'a_plan_b', 'a_plan_e', 'a_kickoff', 'a_design_b', 'a_design_e', 'a_dev_b', 'a_dev_e', 'a_uat_b', 'a_uat_e', 'a_launch', 'a_close'
            , 'state', 'phase', 'progress', 'priority', 'CBU_str', 'pm' ]
