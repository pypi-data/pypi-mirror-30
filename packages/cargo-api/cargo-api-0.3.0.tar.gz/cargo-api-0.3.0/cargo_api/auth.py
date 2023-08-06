import jwt

ADMIN_SCOPE = 'admin'


def decode_token(encoded_token, secret):
    return jwt.decode(encoded_token, secret, algorithms=['HS256'])


def is_authorized(token, scope, user_id = None):
    if scope not in token['scopes']:
        return False

    # if a user_id is supplied, make sure the token belongs to the right user or the token possesses the admin scope
    # See https://cargoone.atlassian.net/wiki/spaces/EN/pages/497811472/Authorization
    if user_id is not None and user_id != token['sub'] and ADMIN_SCOPE not in token['scopes']:
        return False

    return True