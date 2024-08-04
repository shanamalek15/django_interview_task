from django.urls import path, include, re_path
from .views import *
app_name = 'authentication'
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('users/', UserListView.as_view(), name='users'),
    path('activation-sent/', ActivationSentView.as_view(), name='activation_sent'),
    path('', UserSignInView.as_view(), name='signin'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
            UserActivationConfirmView.as_view(), name='user-activation'),

]
