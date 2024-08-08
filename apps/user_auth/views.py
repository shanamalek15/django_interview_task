from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView, \
    ListView, UpdateView,DeleteView,CreateView
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.urls import reverse_lazy
from .mixins import AdminRequiredMixin
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import get_user_model
User = get_user_model()
class UserSignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('authentication:activation_sent')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        print('current_site: ', current_site)
        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        print('uid: ', uid)
        token = account_activation_token.make_token(user)
        print('token: ', token)
        activation_link = self.request.build_absolute_uri(reverse('authentication:user-activation', 
                    kwargs={'uidb64': uid, 'token': token}))
        print('activation_link: ', activation_link)
        message = render_to_string('account_activation_mail.html', {
            'user': user,
            'domain': current_site.domain,
            'activation_link': activation_link,
        })
        from_email = settings.EMAIL_HOST_USER

        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, from_email, to=[to_email])
        email.content_subtype = 'html'
        email.send()
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})
    
    
class ActivationSentView(TemplateView):
    template_name = 'sent_activation.html'


class UserSignInView(FormView):
    template_name = 'signin.html'
    form_class = EmailLoginForm
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        return redirect('product:product-list')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    
    
class UserActivationConfirmView(View):

    def get(self, request, uidb64, token):
        print("uidb64", token, uidb64)
        try:  
            uid = urlsafe_base64_decode(uidb64).decode()
            print('uid: ', uid)
            user = User.objects.get(pk=int(uid))
            print('user: ', user)
            print('user: ', user)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
            user = None
            return HttpResponse("Link Invalid")
        if user is not None and account_activation_token.check_token(user, token):  
            user.is_active = True  
            user.save()  
            messages.success(request, 'Your account has been activated. You can now log in.')
            return redirect(reverse_lazy('authentication:signin'))
        else:
            messages.error(request, 'Activation link is invalid.')
        # except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Activation link is invalid.')
        return HttpResponse("Link Invalid")
    
    
class UserListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'users_list.html'
    context_object_name = 'users'
    paginate_by = 10


# Ensure you have a form defined for the user
class UserCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('authentication:user-list') 
    
class UserUpdateView(AdminRequiredMixin,LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('authentication:user-list')  # Redirect to the list view after updating
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['password'].required = False  # Password is not required on update
        return form

class UserDeleteView(AdminRequiredMixin,LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('authentication:user-list')