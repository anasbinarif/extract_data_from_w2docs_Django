from django.urls import path
from .views import register_user, user_login, user_logout, file_upload_view

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('upload/', file_upload_view, name='file_upload'),
]
