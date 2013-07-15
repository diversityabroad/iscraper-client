from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(required=False)
    start = forms.IntegerField(min_value=1, initial=1, required=False,
            error_messages={ 'invalid':"Page must be a positive integer."})