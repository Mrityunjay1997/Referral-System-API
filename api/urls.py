import os
from django.contrib import admin
from .views_authentication import *
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg.generators import OpenAPISchemaGenerator


admin.autodiscover()
app_name = 'api'


class SchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super(SchemaGenerator, self).get_schema(request, public)
        schema.basePath = os.path.join(schema.basePath, 'api/')
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title = "Referal system",
        description = "Referal system ",
        default_version = "1.0.0",
    ),
    public = True,
    permission_classes = (permissions.AllowAny,),
    urlconf = 'api.urls',
    generator_class = SchemaGenerator
)


urlpatterns = [

    ## Documentation
    re_path(r'^swagger-schema/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^documentation/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    ## Authentication
    re_path(r'user-login/$', LoginView.as_view(), name='login'),
    re_path(r'signup/$', SignupCustomerView.as_view(), name='signup_customer'),
    
    re_path(r'logout/$', LogoutView.as_view(), name='logout'),
   
    re_path(r'get-profile-details/$', GetProfileDetails.as_view(), name='get_profile_details'),

    
    re_path(r'referred-user-lists/$', GetRefereedUserList.as_view(), name='referred_user_list'),

   
]
