import requests

from functools import wraps

from django.conf import settings


def check_recaptcha(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'GET':
            recaptcha_response = request.GET.get('g-recaptcha-response')
            if recaptcha_response:
                data = {
                    'secret': settings.GOOGLE_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                try:
                    r.raise_for_status()
                    result = r.json()
                    if result.get('success', False):
                        request.recaptcha_is_valid = True
                    else:
                        request.recaptcha_is_valid = False
                except:
                    request.recaptcha_is_valid = False
            else:
                request.recaptcha_is_valid = True
        return view_func(request, *args, **kwargs)

    return _wrapped_view
