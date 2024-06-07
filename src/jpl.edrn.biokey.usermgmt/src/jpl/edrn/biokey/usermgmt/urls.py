# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: URL patterns.'''


from .views import reset_password, reset_password_form
from django.urls import path


urlpatterns = [
    path('pwreset/<slug:consortium>/<str:uid>/', reset_password, name='pwreset'),
    path('pwreset/<slug:consortium>/<str:uid>/<str:token>', reset_password_form, name='pwreset_token'),
]
