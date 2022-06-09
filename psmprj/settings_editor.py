# editor related settings#

from . import env

#form templates
CRISPY_TEMPLATE_PACK = 'bootstrap4'


#ckeditor 
# CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Custom',
#         'toolbar_Custom': [
#             ['Bold', 'Italic', 'Underline', 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'RemoveFormat', 'Source']
#         ],
#         'removePlugins': 'toolbar',
#         'toolbarCanCollapse' : True,     
#         'width': 700,
#     },
# }
# django-richtextfield
#         'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link'
# DJRICHTEXTFIELD_CONFIG = {
#     'js': ['//cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js'],
#     'init_template': 'djrichtextfield/init/tinymce.js',
#     # 'settings': {  #TinyMCE
#     #     'menubar': False,
#     #     'plugins': 'link image',
#     #     'toolbar': 'bold italic | link image | removeformat',
#     #     'width': 700
#     # },
#     'settings': {  # CKEditor
#         'toolbar': [
#             {'items': ['Format', '-', 'Bold', 'Italic', '-',
#                     'RemoveFormat']},
#             {'items': ['Link', 'Unlink', 'Image', 'Table']},
#             {'items': ['Source']}
#         ],
#         'format_tags': 'p;h1;h2;h3',
#         'width': 700
#     }    
# }
