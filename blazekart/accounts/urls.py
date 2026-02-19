from django.urls import path
from . import views

urlpatterns=[
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('activate/<uid>/<token>/',views.activate,name='activate'),
    path('logout/',views.logout,name='logout'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('reset_password_validate/<uid>/<token>/',views.reset_password_validate,name='reset_password_validate'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('change-password/',views.change_password,name='change_password'),
    path('sign_in/',views.signin,name='plz_login'),

]