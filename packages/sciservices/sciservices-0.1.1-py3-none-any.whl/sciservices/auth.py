from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import auth as django_auth
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib.auth import logout
from rest_framework import authentication, exceptions
from django.conf import settings

import jwt
import base64
import logging
logger = logging.getLogger(__name__)


def sciuser_required(function):

    def wrap(request, *args, **kwargs):

        # Validates the JWT and returns its payload if valid.
        jwt_payload = validate_jwt(request)

        # User is both logged into this app and via JWT.
        if request.user.is_authenticated() and jwt_payload is not None:

            # Ensure the email matches
            if request.user.username != jwt_payload['email']:
                logger.warning('Django and JWT email mismatch! Log them out and redirect to log back in')
                return logout_redirect(request)

            return function(request, *args, **kwargs)

        # User has a JWT session open but not a Django session. Start a Django session and continue the request.
        elif not request.user.is_authenticated() and jwt_payload is not None:
            if jwt_login(request, jwt_payload):
                return function(request, *args, **kwargs)
            else:
                return logout_redirect(request)
        # User doesn't pass muster, throw them to the login app.
        else:
            return logout_redirect(request)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def validate_jwt(request):
    """
    Determines if the JWT is valid based on expiration and signature evaluation.
    :param request:
    :return: None if JWT is invalid or missing.
    """
    # Extract JWT token into a string.
    jwt_string = request.COOKIES.get("DBMI_JWT", None)

    # Check that we actually have a token.
    if jwt_string is not None:

        # Attempt to validate the JWT (Checks both expiry and signature)
        try:
            payload = jwt.decode(jwt_string,
                                 base64.b64decode(settings.AUTH0_SECRET, '-_'),
                                 algorithms=['HS256'],
                                 leeway=120,
                                 audience=settings.AUTH0_CLIENT_ID)

        except jwt.InvalidTokenError:
            logger.error("Invalid JWT Token")
            payload = None

        except jwt.ExpiredSignatureError:
            logger.error("JWT Expired")
            payload = None
    else:
        payload = None

    return payload


def jwt_login(request, jwt_payload):
    """
    The user has a valid JWT but needs to log into this app. Do so here and return the status.
    :param request:
    :param jwt_payload: String form of the JWT.
    :return:
    """
    logger.debug("Logging user in via JWT. Is Authenticated? " + str(request.user.is_authenticated()))

    # Log them in
    request.session['profile'] = jwt_payload
    user = django_auth.authenticate(**jwt_payload)

    if user:
        login(request, user)
        logger.debug("User logged in")
    else:
        logger.error("Could not log user in")

    return request.user.is_authenticated()


def logout_redirect(request):
    """
    This will log a user out and redirect them to log in again via the AuthN server.
    :param request:
    :return: The response object that takes the user to the login page. 'next' parameter set to bring them back to their intended page.
    """
    logout(request)
    response = redirect(settings.AUTHENTICATION_LOGIN_URL + "?next=" + request.build_absolute_uri())
    response.delete_cookie('DBMI_JWT', domain=settings.COOKIE_DOMAIN)

    return response


class Auth0Authentication(object):

    def authenticate(self, **token_dictionary):
        logger.debug("Attempting to Authenticate User.")

        try:
            user = get_user_model().objects.get(username=token_dictionary["email"])

        except User.DoesNotExist:
            logger.debug("User not found, creating.")

            user = User(username=token_dictionary["email"], email=token_dictionary["email"])
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        try:
            # Get the JWT token from the header.
            jwt_string = request.META.get('HTTP_AUTHORIZATION', None)

            # Check for token and return None if not
            if jwt_string is None:
                logger.exception('No JWT token')
                return None

            # Trim the prefix.
            jwt_string = jwt_string[len('JWT '):]

            # Attempt to validate the token.
            payload = jwt.decode(jwt_string,
                                 base64.b64decode(settings.AUTH0_SECRET, '-_'),
                                 algorithms=['HS256'],
                                 audience=settings.AUTH0_CLIENT_ID)

            # Get the email.
            email = payload['email']

            # Do the query.
            user = get_user_model().objects.get(email=email)

            return user, None

        except User.DoesNotExist as e:
            logger.exception('Exception: {}'.format(e))
            raise exceptions.AuthenticationFailed('User does not exist')

        except KeyError as e:
            logger.exception('Exception: {}'.format(e))
            raise exceptions.AuthenticationFailed('JWT token is malformed/did not include user email')

        except jwt.InvalidTokenError as e:
            logger.exception('Exception: {}'.format(e))
            raise exceptions.AuthenticationFailed('Missing/Invalid JWT Token')

        except jwt.ExpiredSignatureError as e:
            logger.exception('Exception: {}'.format(e))
            raise exceptions.AuthenticationFailed('Expired JWT Token')

    @staticmethod
    def headers(token):
        return {"Authorization": 'JWT {}'.format(token), 'Content-Type': 'application/json'}
