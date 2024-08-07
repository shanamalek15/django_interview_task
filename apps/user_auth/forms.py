from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

User = get_user_model()

class SignupForm(UserCreationForm):  
    email = forms.EmailField(max_length=200, help_text='Required')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required') 
    class Meta:  
        model = User  
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
        
        
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Leave blank if you don't want to change it.")

    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'role': forms.Select(attrs={'required': 'required'}),
            'first_name': forms.TextInput(attrs={'required': 'required'}),
            'last_name': forms.TextInput(attrs={'required': 'required'}),
            'password': forms.PasswordInput(attrs={'required': 'required'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.instance.pk:
            if not password:
                return self.instance.password
            elif password == self.instance.password:
                return self.instance.password
            else:
                return make_password(password)
        else:
            return make_password(password)
            
class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError('Invalid login credentials')
        self.cleaned_data['user'] = user
        return self.cleaned_data