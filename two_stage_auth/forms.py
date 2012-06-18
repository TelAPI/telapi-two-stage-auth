from django import forms


CONTACT_METHODS = (
    (1, u'SMS'),
    (2, u'Voice'),
    )


class GenerateTokenForm(forms.Form):
    username = forms.CharField(max_length=20)
    phone_number = forms.CharField(max_length=20)
    contact_method = forms.ChoiceField(choices=CONTACT_METHODS)


class TokenLoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    token = forms.CharField(max_length=10)

