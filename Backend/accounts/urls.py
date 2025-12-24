from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('check-username/', views.check_username, name='check_username'),
    path('user/', views.user_info, name='user_info'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
]
