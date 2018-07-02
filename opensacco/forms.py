from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150,)
    email = forms.EmailField(max_length=150,)
    phone = forms.CharField(max_length=50,)
    message = forms.CharField(widget=forms.Textarea)



