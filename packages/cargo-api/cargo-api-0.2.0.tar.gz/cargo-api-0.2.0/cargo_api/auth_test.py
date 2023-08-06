import unittest
import jwt

from auth import decode_token, is_authorized


class TestAuth(unittest.TestCase):

    def test_decode_token(self):
        test_id = 'test123'
        secret = 'secret'
        payload = {
            'test': test_id
        }

        encoded_token = jwt.encode(payload, secret, algorithm='HS256')

        token = decode_token(encoded_token, secret)
        self.assertEqual(token['test'], test_id)

    def test_authorization(self):
        payload = {
            'scopes': ['test:read', 'test:write', 'test:delete']
        }
        secret = 'secret'
        encoded_token = jwt.encode(payload, secret, algorithm='HS256')

        self.assertTrue(is_authorized(decode_token(encoded_token, secret), 'test:write'))
        self.assertFalse(is_authorized(decode_token(encoded_token, secret), 'test:error'))

    def test_authorization_with_user_id(self):
        payload = {
            'scopes': ['test:read', 'test:write', 'test:delete'],
            'sub': 'user123'
        }
        secret = 'secret'
        encoded_token = jwt.encode(payload, secret, algorithm='HS256')

        self.assertTrue(is_authorized(decode_token(encoded_token, secret), 'test:write', 'user123'))
        self.assertFalse(is_authorized(decode_token(encoded_token, secret), 'test:error', 'wrong_user'))


if __name__ == '__main__':
    unittest.main()