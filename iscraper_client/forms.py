from django import forms


class SearchForm(forms.Form):

    q = forms.CharField(required=False)
    iframe = forms.CharField(required=False)  # Boolean field doesn;t work???
    page = forms.IntegerField(
        min_value=1, initial=1, required=False,
        error_messages={'invalid': "Page must be a positive integer."})
    page_local = forms.IntegerField(
        min_value=1, initial=1, required=False,
        error_messages={'invalid': "Page must be a positive integer."})


class DualSearchForm(forms.Form):

    q = forms.CharField(required=False)
    iframe = forms.CharField(required=False)
    page_one = forms.IntegerField(
        min_value=1, initial=1, required=False,
        error_messages={'invalid': "Page must be a positive integer."})
    page_two = forms.IntegerField(
        min_value=1, initial=1, required=False,
        error_messages={'invalid': "Page must be a positive integer."})
