import mock
import requests
from requests.exceptions import HTTPError
import unittest
import webtest
from urllib.parse import parse_qs, urlparse

import kinto.core
from kinto.core.errors import ERRORS
from kinto.core.testing import FormattedErrorMixin
from kinto.core.utils import random_bytes_hex
from pyramid.config import Configurator
from time import sleep

from kinto_facebook import __version__ as kinto_facebook_version


def get_request_class(prefix):

    class PrefixedRequestClass(webtest.app.TestRequest):

        @classmethod
        def blank(cls, path, *args, **kwargs):
            path = '/%s%s' % (prefix, path)
            return webtest.app.TestRequest.blank(path, *args, **kwargs)

    return PrefixedRequestClass


class BaseWebTest(object):
    """Base Web Test to test your cornice service.

    It setups the database before each test and delete it after.
    """

    api_prefix = "v1"

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self._get_test_app()
        self.headers = {
            'Content-Type': 'application/json',
        }
        self._facebook_verify_patcher = mock.patch('kinto_facebook.authentication.requests')

    def setUp(self):
        super(BaseWebTest, self).setUp()
        self.facebook_verify = self._facebook_verify_patcher.start()
        self.facebook_verify.get.return_value.json.return_value = {
            'data': {
                'user_id': 'bob'
            }
        }

    def tearDown(self):
        super(BaseWebTest, self).tearDown()
        self._facebook_verify_patcher.stop()

    def _get_test_app(self, settings=None):
        config = self._get_app_config(settings)
        wsgi_app = config.make_wsgi_app()
        app = webtest.TestApp(wsgi_app)
        app.RequestClass = get_request_class(self.api_prefix)
        return app

    def _get_app_config(self, settings=None):
        config = Configurator(settings=self.get_app_settings(settings))
        kinto.core.initialize(config, version='1.0.0')
        return config

    def get_app_settings(self, additional_settings=None):
        settings = kinto.core.DEFAULT_SETTINGS.copy()
        settings['project_name'] = 'kinto'
        settings['includes'] = 'kinto_facebook'
        settings['multiauth.policies'] = 'facebook'
        authn = 'kinto_facebook.authentication.FacebookAuthenticationPolicy'
        settings['multiauth.policy.facebook.use'] = authn
        settings['cache_backend'] = 'kinto.core.cache.memory'
        settings['userid_hmac_secret'] = random_bytes_hex(16)
        settings['facebook.relier.enabled'] = True
        settings['facebook.webapp.authorized_domains'] = ['*.firefox.com']

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings


class DeactivatedRelierTest(BaseWebTest, unittest.TestCase):
    def get_app_settings(self, additional_settings=None):
        settings = super(DeactivatedRelierTest, self).get_app_settings()
        settings['facebook.relier.enabled'] = False
        return settings

    def test_login_view_is_not_available(self):
        self.app.get('/facebook/login', status=404)

    def test_token_view_is_not_available(self):
        self.app.get('/facebook/token', status=404)


class LoginViewTest(BaseWebTest, unittest.TestCase):
    url = '/facebook/login?redirect=https://readinglist.firefox.com'

    def get_app_settings(self, additional_settings=None):
        additional_settings = additional_settings or {}
        additional_settings.update({
            'facebook.client_id': 'cid',
            'facebook.client_secret': 'csecret',
            'facebook.app_access_token': 'app_token'
        })
        return super(LoginViewTest, self).get_app_settings(additional_settings)

    def test_redirect_parameter_is_mandatory(self):
        url = '/facebook/login'
        r = self.app.get(url, status=400)
        self.assertIn('redirect', r.json['message'])

    def test_redirect_parameter_should_be_refused_if_not_whitelisted(self):
        url = '/facebook/login?redirect=http://not-whitelisted.tld'
        r = self.app.get(url, status=400)
        self.assertIn('redirect', r.json['message'])

    def test_redirect_parameter_should_be_accepted_if_whitelisted(self):
        with mock.patch.dict(self.app.app.registry.settings,
                             [('facebook.webapp.authorized_domains',
                               '*.whitelist.ed')]):
            url = '/facebook/login?redirect=http://iam.whitelist.ed'
            self.app.get(url)

    def test_redirect_parameter_should_be_rejected_if_no_whitelist(self):
        with mock.patch.dict(self.app.app.registry.settings,
                             [('facebook.webapp.authorized_domains',
                               '')]):
            url = '/facebook/login?redirect=http://iam.whitelist.ed'
            r = self.app.get(url, status=400)
        self.assertIn('redirect', r.json['message'])

    def test_login_view_persists_state(self):
        r = self.app.get(self.url)
        url = r.headers['Location']
        url_fragments = urlparse(url)
        queryparams = parse_qs(url_fragments.query)
        state = queryparams['state'][0]
        self.assertEqual(self.app.app.registry.cache.get(state),
                         'https://readinglist.firefox.com')

    def test_login_view_persists_state_with_expiration(self):
        r = self.app.get(self.url)
        url = r.headers['Location']
        url_fragments = urlparse(url)
        queryparams = parse_qs(url_fragments.query)
        state = queryparams['state'][0]
        self.assertGreater(self.app.app.registry.cache.ttl(state), 299)
        self.assertLessEqual(self.app.app.registry.cache.ttl(state), 300)

    def test_login_view_persists_state_with_expiration_from_settings(self):
        r = self.app.get(self.url)
        url = r.headers['Location']
        url_fragments = urlparse(url)
        queryparams = parse_qs(url_fragments.query)
        state = queryparams['state'][0]
        self.assertGreater(self.app.app.registry.cache.ttl(state), 299)
        self.assertLessEqual(self.app.app.registry.cache.ttl(state), 300)

    @mock.patch('kinto_facebook.views.uuid.uuid4')
    def test_login_view_redirects_to_authorization(self, mocked_uuid):
        mocked_uuid.return_value = mock.MagicMock(hex='1234')
        settings = self.app.app.registry.settings
        auth_endpoint = settings.get('facebook.authorization_endpoint')
        client_id = settings.get('facebook.client_id')
        redirect_uri = 'http%3A%2F%2Flocalhost%2Fv1%2Ffacebook%2Ftoken'
        expected_redirect = '{}?client_id={}&redirect_uri={}&state=1234'.format(auth_endpoint,
                                                                                client_id,
                                                                                redirect_uri)

        r = self.app.get(self.url)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers['Location'], expected_redirect)


class TokenViewTest(FormattedErrorMixin, BaseWebTest, unittest.TestCase):
    url = '/facebook/token'
    login_url = '/facebook/login?redirect=https://readinglist.firefox.com'

    def __init__(self, *args, **kwargs):
        super(TokenViewTest, self).__init__(*args, **kwargs)
        self._facebook_trade_patcher = mock.patch('kinto_facebook.views.requests')

    def setUp(self):
        super(BaseWebTest, self).setUp()
        self.facebook_trade = self._facebook_trade_patcher.start()
        self.facebook_trade.get.return_value.json.return_value = {"access_token": "oauth-token"}

    def tearDown(self):
        super(BaseWebTest, self).tearDown()
        self._facebook_trade_patcher.stop()

    def test_fails_if_no_ongoing_session(self):
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        resp = self.app.get(url, status=408)
        error_msg = 'The Facebook Auth session was not found, please re-authenticate.'
        self.assertFormattedError(
            resp, 408, ERRORS.MISSING_AUTH_TOKEN, "Request Timeout", error_msg)

    def test_fails_if_state_or_code_is_missing(self):
        headers = {'Cookie': 'state=abc'}
        for params in ['', '?state=abc', '?code=1234']:
            r = self.app.get(self.url + params, headers=headers, status=400)
            self.assertIn('Required', r.json['message'])

    def test_fails_if_state_does_not_match(self):
        self.app.app.registry.cache.set('def', 'http://foobar', ttl=1)
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        resp = self.app.get(url, status=408)
        error_msg = 'The Facebook Auth session was not found, please re-authenticate.'
        self.assertFormattedError(
            resp, 408, ERRORS.MISSING_AUTH_TOKEN, "Request Timeout", error_msg)

    def test_fails_if_state_was_already_consumed(self):
        self.app.app.registry.cache.set('abc', 'http://foobar', ttl=1)
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        self.app.get(url)
        resp = self.app.get(url, status=408)
        error_msg = 'The Facebook Auth session was not found, please re-authenticate.'
        self.assertFormattedError(
            resp, 408, ERRORS.MISSING_AUTH_TOKEN, "Request Timeout", error_msg)

    def test_fails_if_state_has_expired(self):
        with mock.patch.dict(self.app.app.registry.settings,
                             [('facebook.cache_ttl_seconds', 0.01)]):
            r = self.app.get(self.login_url)
        url = r.headers['Location']
        url_fragments = urlparse(url)
        queryparams = parse_qs(url_fragments.query)
        state = queryparams['state'][0]
        url = '{url}?state={state}&code=1234'.format(state=state, url=self.url)
        sleep(0.02)
        resp = self.app.get(url, status=408)
        error_msg = 'The Facebook Auth session was not found, please re-authenticate.'
        self.assertFormattedError(
            resp, 408, ERRORS.MISSING_AUTH_TOKEN, "Request Timeout", error_msg)

    def tests_redirects_with_token_traded_against_code(self):
        self.app.app.registry.cache.set('abc', 'http://foobar?token=', ttl=1)
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        r = self.app.get(url)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers['Location'],
                         'http://foobar?token=oauth-token')

    def tests_return_503_if_facebook_auth_server_behaves_badly(self):
        self.facebook_trade.get.return_value.raise_for_status.side_effect = HTTPError
        self.facebook_trade.exceptions.HTTPError = HTTPError

        self.app.app.registry.cache.set('abc', 'http://foobar', ttl=1)
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        self.app.get(url, status=503)

    def tests_return_400_if_client_error_detected(self):
        httpBadRequest = mock.MagicMock()
        httpBadRequest.status_code = 400
        httpBadRequest.json.return_value = {"error": "blah"}
        self.facebook_trade.get.return_value = httpBadRequest

        self.app.app.registry.cache.set('abc', 'http://foobar', ttl=1)
        url = '{url}?state=abc&code=1234'.format(url=self.url)
        self.app.get(url, status=400)


class CapabilityTestView(BaseWebTest, unittest.TestCase):

    def test_facebook_capability(self, additional_settings=None):
        resp = self.app.get('/')
        capabilities = resp.json['capabilities']
        self.assertIn('facebook', capabilities)
        expected = {
            "version": kinto_facebook_version,
            "url": "https://github.com/Kinto/kinto-facebook",
            "description": "You can authenticate to that server using "
                           "Facebook Auth."
        }
        self.assertEqual(expected, capabilities['facebook'])
