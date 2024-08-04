from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class SignupForm(UserCreationForm):  
    email = forms.EmailField(max_length=200, help_text='Required')  
    class Meta:  
        model = User  
        fields = ('email', 'password1', 'password2')  
        
        
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank if you don't want to change it.")

    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'role': forms.Select(attrs={'required': 'required'}),
            'first_name': forms.TextInput(attrs={'required': 'required'}),
            'last_name': forms.TextInput(attrs={'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except password
        for field in self.fields:
            if field != 'password':
                self.fields[field].required = True
        
        # If updating user, show hashed password
        if self.instance.pk:
            # self.fields['password'].widget.attrs['readonly'] = True
            self.fields['password'].help_text = "This is the hashed value of the password. You can leave this as is or change it to update the password."

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.instance.pk:
            # Update view, password is not required
            if not password or password == self.instance.password:
                return self.instance.password
        # Create view or password is being changed
        return make_password(password)
            
class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError('Invalid email or password')
        return self.cleaned_data