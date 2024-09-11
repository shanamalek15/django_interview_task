from django.urls import path, include, re_path
from .views import *
from django.contrib.auth.views import LogoutView

app_name = 'authentication'
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/update/<int:pk>', UserUpdateView.as_view(), name='user-update'),
    path('users/delete/<int:pk>', UserDeleteView.as_view(), name='user-delete'),
    path('activation-sent/', ActivationSentView.as_view(), name='activation_sent'),
    path('', UserSignInView.as_view(), name='signin'),
    path('logout/', LogoutView.as_view(next_page='authentication:signin'), name='logout'),
    # re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', UserActivationConfirmView.as_view(), name='activate'),
    path('activate/<uidb64>/<token>/',  UserActivationConfirmView.as_view(), name='user-activation'),
    path('resend-activation/', ResendActivationLinkView.as_view(), name='resend_activation'),

]
