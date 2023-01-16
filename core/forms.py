from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)



class QuestionForm(forms.Form):
    answer = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.test = kwargs.pop('test')
        super().__init__(*args, **kwargs)



