import jwt


def decode_token(encoded_token, secret):
    return jwt.decode(encoded_token, secret, algorithms=['HS256'])


def is_authorized(token, scope, user_id = None):
    if scope not in token['scopes']:
        return False

    if user_id is not None and user_id != token['sub']:
        return False

    return True