from django.contrib.auth.models import User
from base import BaseTestCase
from test_project.testapp.models import StrictlyComment
from voting.models import Vote

class TestValidationStrictlyComment(BaseTestCase):
    def setUp(self):
        super(TestValidationStrictlyComment, self).setUp()
        self.assistant_client = self.get_assistant_client()

        self.assertEqual(StrictlyComment.objects.create(
            author = User.objects.get(username='oduvan'),
            text = 'Hello, my assistant'
        ).pk,1)

        self.assertEqual(StrictlyComment.objects.create(
            author = User.objects.get(username='assistant'),
            text = 'Hi, oduvan'
        ).pk,2)

        self.assertEqual(Vote.get_votes_range(
            obj = StrictlyComment.objects.get(id=2),
            user = User.objects.get(username='oduvan')
        ), [-1, 0, 1])

    def test_it(self):
        self.assertEqualGetResponseJson('/vote/testapp/strictlycomment/2/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqualGetResponseJson('/vote/testapp/strictlycomment/2/up/2/',
            {u'error_message': u"Vote out of range", u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/strictlycomment/1/up/',
            {u'error_message': u"Author can't for his comment", u'success': False})

        self.assertEqualGetResponseJson('/vote/testapp/strictlycomment/2/up/',
            {u'error_message': u"Author can't for his comment", u'success': False}, client=self.assistant_client)

        self.assertEqualGetResponseJson('/vote/testapp/strictlycomment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True}, client=self.assistant_client)

    def test_user_vote(self):
        self.assertEqualGetResponseJson('/vote/auth/user/2/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqualGetResponseJson('/vote/auth/user/1/up/',
            {u'error_message': u"You can't vote for yourself", u'success': False})
