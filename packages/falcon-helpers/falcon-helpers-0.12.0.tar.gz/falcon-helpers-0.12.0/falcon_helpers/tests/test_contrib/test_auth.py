import jwt
import falcon_helpers as fh


def test_generate_auth_token():
    u1 = fh.contrib.auth.User.testing_create()

    token = u1.generate_auth_token('aud', 'secret')
    result = jwt.decode(token, 'secret', algorithm='HS256', audience='aud')
    assert result['sub'] == u1.ident

    token = u1.generate_auth_token('aud', 'secret', additional_data={
        'other': 'true'
    })
    result = jwt.decode(token, 'secret', algorithm='HS256', audience='aud')
    assert result['sub'] == u1.ident
    assert result['other'] == 'true'
