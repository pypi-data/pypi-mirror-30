"""
Manages interface with biobank system.
"""
import requests
from django.contrib.auth import authenticate, login, get_user
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from rest_framework.authtoken.models import Token

from biobank.conf import settings
from django.conf import settings as djangoSettings
from django.contrib.auth.models import User
from oauth_tokens.models import AccessToken, UserCredentials
from rest_framework import authentication
from oauth2_provider.middleware import OAuth2TokenMiddleware


class BiobankBackend:
    provider_name = 'biobank'

    def __init__(self):
        self.provider_name = BiobankBackend.provider_name
        pass

    def authenticate(self, username=None, password=None, token=None):
        print(token)
        try:
            user = User.objects.get(username=username)
            if token:
                person = self.get_user_from_api(token, True)
                self.update_user(person, user)
                return user
            token = self.get_token(username)
            if not token:
                response = self.request_token(username, password)
                print(response)
                if not response:
                    return None
                token = self.create_token(response, user)

            person = self.get_user_from_api(token.access_token)
            self.update_user(person, user)
            return user
        except User.DoesNotExist:
            if token:
                person = self.get_user_from_api(token, True)
                if not person:
                    return None
                user = User.objects.get(username=person['email'])
                if not user:
                    user = self.create_user(person['email'])
                self.update_user(person, user)
                return user
            response = self.request_token(username, password)
            if not response:
                return None
            user = self.create_user(username)
            token = self.create_token(response, user)
            person = self.get_user_from_api(token.access_token)
            self.update_user(person, user)
            return user

    def get_user_from_api(self, token, bearer=False):
        header_token = 'Bearer {}'.format(token)
        if bearer:
            header_token = token
        headers = {'Authorization': header_token}
        r = requests.get(settings.API_URL + '/users/me', headers=headers)
        if r.status_code == requests.codes.ok:
            response = r.json()
            return response['results']['data']
        return None

    def create_user(self, email):
        user = User(username=email)
        user.save()
        return user

    def update_user(self, person, user):
        user.first_name = person['firstName']
        user.last_name = person['lastName']
        user.email = person['email']
        user.save()

    def request_token(self, username, password):
        r = requests.post(settings.API_URL + '/oauth/token',
                          data={'username': username, 'password': password,
                                'client_id': settings.CLIENT_ID,
                                'client_secret': settings.CLIENT_SECRET,
                                'grant_type': settings.CLIENT_GRANT,
                                })
        if r.status_code == requests.codes.ok:
            return r.json()
        return None

    def create_token(self, data, user):
        try:
            user_credentials = UserCredentials.objects.get(provider=self.provider_name, username=user.username)
            AccessToken.objects.filter(provider=self.provider_name, user_credentials=user_credentials).delete()
        except UserCredentials.DoesNotExist:
            user_credentials = UserCredentials(provider=self.provider_name, username=user.username)
            user_credentials.save()
        access_token = AccessToken(provider=self.provider_name, access_token=data['access_token'],
                                   refresh_token=data['refresh_token'], expires_in=data['expires_in'],
                                   token_type=data['token_type'], user_credentials=user_credentials)
        access_token.user_id = user.pk
        access_token.save()
        return access_token

    @staticmethod
    def get_token(email):
        try:
            user_credentials = UserCredentials.objects.get(provider=BiobankBackend.provider_name, username=email)
            access_token = AccessToken.objects.filter(provider=BiobankBackend.provider_name,
                                                      user_credentials=user_credentials).latest()
        except (AccessToken.DoesNotExist, UserCredentials.DoesNotExist):
            return None

        return access_token

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class BiobankRequestBackend(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        bb = BiobankBackend()
        user = bb.authenticate(token=token)
        if user:
            Token.objects.get_or_create(user=user)
        return user


class TokenAuthSupportQueryString(authentication.TokenAuthentication):

    def authenticate(self, request):
        token = request.GET.get("token") or request.query_params.get('token')
        # Check if 'token_auth' is in the request query params.
        # Give precedence to 'Authorization' header.
        if token:
            return self.authenticate_credentials(token)
        else:
            return super(TokenAuthSupportQueryString, self).authenticate(request)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class AccessTokenQueryBackend(authentication.TokenAuthentication):

    def authenticate(self, request):
        if isinstance(request, WSGIRequest):
            token = request.GET.get("token")
        else:
            token = request.query_params.get('token')
        # Check if 'token_auth' is in the request query params.
        # Give precedence to 'Authorization' header.
        if token:
            return self.authenticate_credentials(token)[0]
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class BiobankMiddleware(object):

    def process_request(self, request):
        if isinstance(request, WSGIRequest):
            token = request.GET.get("token")
        else:
            token = request.query_params.get('token')
        if token:
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
                    login(request, user)
