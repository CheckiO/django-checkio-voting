from django.contrib.auth.models import User
from django.utils.unittest import TestCase
from test_project.testapp.models import Comment
from voting.models import Vote


class CalculationTest(TestCase):
    def setUp(self):
        self.u_oduvan = User.objects.create_user('oduvan', 'alexander@lyabah.com','none')
        self.u_assistant = User.objects.create_user('assistant', 'assistant@checkio.org','none')
        self.comment = Comment.objects.create(author=self.u_oduvan, text='OH')

    def test_get_score(self):
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 0, 'score': 0})
        self.assertFalse(Vote.objects.get_for_user(self.comment, self.u_oduvan))
        self.assertFalse(Vote.objects.get_for_user(self.comment, self.u_assistant))

        Vote.objects.record_vote(self.comment, self.u_oduvan, 1)
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 1, 'score': 1})

        Vote.objects.record_vote(self.comment, self.u_oduvan, 0)
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 1, 'score': 0})

        Vote.objects.record_vote(self.comment, self.u_oduvan, -1)
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 1, 'score': -1})

        Vote.objects.record_vote(self.comment, self.u_assistant, -1)
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 2, 'score': -2})

        Vote.objects.record_vote(self.comment, self.u_oduvan, 1)
        self.assertEqual(Vote.objects.get_score(self.comment),{'num_votes': 2, 'score': 0})

        self.assertEqual(Vote.objects.get_for_user(self.comment, self.u_oduvan).vote, 1)
        self.assertEqual(Vote.objects.get_for_user(self.comment, self.u_assistant).vote, -1)
