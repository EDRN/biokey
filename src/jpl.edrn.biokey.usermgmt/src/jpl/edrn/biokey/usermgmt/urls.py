# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: URL patterns.'''


from .views import reset_password
from django.urls import path


urlpatterns = [
    path('pwreset/<slug:consortium>/<str:uid>/<str:token>', reset_password, name='pwreset')
]
