# tables.py
# import django_tables2 as tables
# from .models import Project
# from common.models import CBU

# class ProjectRequestTable(tables.Table):
#     class Meta:
#         model = Project
#         template_name = "django_tables2/bootstrap.html"

#         fields = ("code", "title", "description" )

        # CBU_list = tables.Column()

        # def render_CBU_list(self, value):
        #     if value is not None:
        #         return ', '.join([CBU.name for category in value.all()])
        #     return '-'