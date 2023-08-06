''' A Module Description '''
from app.User import User
from masonite.facades.Auth import Auth
from entry.api.models.OAuthToken import OAuthToken


class OAuthPasswordGrantController:
    ''' Class Docstring Description '''

def generate(self, Request):
    if not Request.has('username') or not Request.has('password'):
        return {'error': 'This API call requires a username and password in the payload.'}

    user = Auth(Request).login(Request.input(
        'username'), Request.input('password'))

    if user:
        if Request.has('scopes'):
            scopes = Request.input('scopes')
        else:
            scopes = ''

        return {'token': user.create_token(scopes=scopes)}
    else:
        return {'error': 'Incorrect username or password'}

    def revoke(self, Request):
        if not Request.has('token'):
            return {'error': 'Token not received'}

        get_token = OAuthToken.where('token', Request.input('token')).first()
        if get_token:
            get_token.delete()
            return {'success': 'Token was revoked'}
        else:
            return {'error': 'Could not find token'}
