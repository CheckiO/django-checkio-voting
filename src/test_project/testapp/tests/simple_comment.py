from django.contrib.auth.models import User
from testapp.models import Comment, Article
from django.test import  Client
from django.test.utils import override_settings
from voting.exceptions import VoteValidationError
from mock import patch

from base import BaseTestCase
from voting.models import Vote


class SimpleCommentTestBaseErrors(BaseTestCase):

    def test_anonymous(self):
        "Anonymous user's can't vote."

        self.client.logout()

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {u'error_message': u'Anonymous user can not vote', u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/down/',
            {u'error_message': u'Anonymous user can not vote', u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/clear/',
            {u'error_message': u'Anonymous user can not vote', u'success': False})

    def test_model_in_url(self):
        'valid names of app and model in url'

        self.assertEqualGetResponseJson('/vote/unknownapp/comment/1/up/',
            {u'error_message': u'Wrong request. Model.', u'success': False})

        self.assertEqualGetResponseJson('/vote/unknownapp/uknownmodel/1/up/',
            {u'error_message': u'Wrong request. Model.', u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/uknownmodel/1/up/',
            {u'error_message': u'Wrong request. Model.', u'success': False})

    def test_object_in_url(self):
        'valid id of object for current model'

        self.assertEqualGetResponseJson('/vote/testapp/comment/5/up/',
            {u'error_message': u'Wrong request. Object.', u'success': False})

    def test_vote_count(self):
        '''
            VOTING_LAMBDA_VALID_VOTE, VOTING_MAX_VOTE_COUNT, VOTING_MIN_VOTE_COUNT - details in voting.settings
        '''

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/2/',
            {u'error_message': u'Wrong request. Vote is too high.', u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/down/2/',
            {u'error_message': u'Wrong request. Vote is too low.', u'success': False})

    def check_author(vote):
        from voting.settings import default_valid_vote
        default_valid_vote(vote)
        if vote.object.author == vote.user:
            raise VoteValidationError, "Author can't vote for itself"

    @override_settings(VOTING_LAMBDA_VALID_VOTE=check_author)
    def test_check_author(self):
        'user defined validation function'

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {u'error_message': u"Author can't vote for itself", u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/2/',
            {u'error_message': u'Wrong request. Vote is too high.', u'success': False})




class SimpleCommentTestSuccess(BaseTestCase):


    def test_success_votes(self):

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/down/',
            {"score": {"score": -1, "num_votes": 1}, "success": True})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/clear/',
            {"score": {"score": 0, "num_votes": 1}, "success": True})

    def test_two_users(self):
        self.client.login(username='oduvan', password='none')

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        assistant_client = self.get_assistant_client()

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 2, "num_votes": 2}, "success": True}, client=assistant_client)

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/down/',
            {"score": {"score": 0, "num_votes": 2}, "success": True}, client=assistant_client)

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/clear/',
            {"score": {"score": 1, "num_votes": 2}, "success": True}, client=assistant_client)


class SimpleCommentTestDirect(BaseTestCase):

    def setUp(self):
        super(SimpleCommentTestDirect, self).setUp()
        self._patcher1 = patch('django.contrib.messages.error')
        self._patcher2 = patch('django.contrib.messages.info')
        self.mock_error = self._patcher1.start()
        self.mock_info = self._patcher2.start()

    def tearDown(self):
        self._patcher1.stop()
        self._patcher2.stop()

    def assertRedirectionUrl(self, resp, redirection_url):
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp._headers.get('location')[1], redirection_url)


    def test_redirection_next_urls(self):

        # settings.VOTING_REDIRECT_VIEW_DEFAULT_URL
        resp = self.client.get('/vote/direct/unknownapp/comment/1/up/')
        self.assertRedirectionUrl(resp, 'http://testserver/main-page/')

        # next paramenter
        resp = self.client.get('/vote/direct/unknownapp/comment/1/up/?next=/unknownapp/')
        self.assertRedirectionUrl(resp, 'http://testserver/unknownapp/')

        resp = self.client.get('/vote/direct/unknownapp/comment/1/up/?next=/unknownapp/', HTTP_REFERER='/knownapp/')
        self.assertRedirectionUrl(resp, 'http://testserver/unknownapp/')

        #getting from referer
        resp = self.client.get('/vote/direct/unknownapp/comment/1/up/', HTTP_REFERER='/knownapp/')
        self.assertRedirectionUrl(resp, 'http://testserver/knownapp/')

    def test_error_message(self):
        self.client.get('/vote/direct/unknownapp/comment/1/up/')
        self.assertEqual(self.mock_error.call_args[0][1], 'Wrong request. Model.')

        self.client.get('/vote/direct/testapp/comment/1/up/2/')
        self.assertEqual(self.mock_error.call_args[0][1], 'Wrong request. Vote is too high.')

    def test_successful(self):
        self.client.get('/vote/direct/testapp/comment/1/up/')
        self.assertFalse(self.mock_error.call_count)
        self.assertEqual(self.mock_info.call_args[0][1], 'You are the best :)')
        self.assertEqual(Vote.objects.get_for_user(Comment.objects.get(pk=1), User.objects.get(username='oduvan')).vote, 1)







