from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView, ListView
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

class UserSignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.is_active = False
        user.save()
        
        # current_site = get_current_site(self.request)
        # mail_subject = 'Activate your account'
        # message = render_to_string('account_activation_email.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token': account_activation_token.make_token(user),
        # })
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage(mail_subject, message, to=[to_email])
        # email.send()
        
        return redirect('authentication:activation_sent')


    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})
    
    
class ActivationSentView(TemplateView):
    template_name = 'sent_activation.html'


class UserSignInView(FormView):
    template_name = 'signin.html'
    form_class = EmailLoginForm
    
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        
        if user is not None:
            login(self.request, user)
            return redirect('product:product-list')  # Redirect to a home or dashboard page
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    
    
class UserActivationConfirmView(View):

    def get(self, request, uidb64, token):
        
        try:  
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)  
            if default_token_generator.check_token(user, token):
                    user.is_active = True
                    user.save()
                    messages.success(request, 'Your account has been activated. You can now log in.')
            else:
                    messages.error(request, 'Activation link is invalid.')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Activation link is invalid.')

        return redirect(reverse_lazy('authentication:signin'))
    
    
class UserListView(ListView):
    model = User
    template_name = 'users_list.html'
    context_object_name = 'users'
    paginate_by = 15
