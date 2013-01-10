from django.contrib.auth.models import User
from base import BaseTestCase
from test_project.testapp.models import Comment, Article


class TestSignals(BaseTestCase):
    def test_signals(self):
        from voting.signals import post_vote

        s_data = {'votes':0}
        def set_last_saved_vote(vote, *args, **kwargs):
            s_data['votes'] += 1
            s_data['last_vote'] = vote.vote

        post_vote.connect(set_last_saved_vote, sender=Comment)

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqual(s_data,{'last_vote': 1, 'votes': 1})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqual(s_data, {'last_vote': 1, 'votes': 1})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/down/',
            {"score": {"score": -1, "num_votes": 1}, "success": True})

        self.assertEqual(s_data, {'last_vote': -1, 'votes': 2})

        assistant_client = self.get_assistant_client()

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 0, "num_votes": 2}, "success": True}, client=assistant_client)

        self.assertEqual(s_data, {'last_vote': 1, 'votes': 3})

        self.assertEqual(Article.objects.create(
            author=User.objects.get(username='oduvan'),
            subject='NEW'
        ).pk,1)

        self.assertEqualGetResponseJson('/vote/testapp/article/1/down/',
            {"score": {"score": -1, "num_votes": 1}, "success": True})

        self.assertEqual(s_data, {'last_vote': 1, 'votes': 3})
        post_vote.disconnect(set_last_saved_vote)

    def test_signals_change_vote(self):
        self.assertEqual(Comment.objects.create(
            author=User.objects.get(username='oduvan'),
            text='CheckiO rules :)'
        ).pk,2)
        from voting.signals import post_vote, pre_vote

        s_data = {}
        def set_last_saved_vote(vote, *args, **kwargs):
            s_data[vote.object.pk] = vote.prev_vote
        pre_vote.connect(set_last_saved_vote, sender=Comment)

        def check_equal_s_data(vote, *args, **kwargs):
            self.assertEqual(s_data[vote.object.pk], vote.prev_vote)
        post_vote.connect(check_equal_s_data, sender=Comment)

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})

        self.assertEqual(s_data,{1:0})

        self.assertEqualGetResponseJson('/vote/testapp/comment/1/clear/',
            {"score": {"score": 0, "num_votes": 1}, "success": True})
        self.assertEqual(s_data,{1:1})

        self.assertEqualGetResponseJson('/vote/testapp/comment/2/up/',
            {"score": {"score": 1, "num_votes": 1}, "success": True})
        self.assertEqual(s_data,{1:1, 2:0})

        self.assertEqualGetResponseJson('/vote/testapp/comment/2/down/',
            {"score": {"score": -1, "num_votes": 1}, "success": True})
        self.assertEqual(s_data,{1:1, 2:1})

        assistant_client = self.get_assistant_client()

        self.assertEqualGetResponseJson('/vote/testapp/comment/2/down/',
            {"score": {"score": -2, "num_votes": 2}, "success": True}, client=assistant_client)
        self.assertEqual(s_data,{1:1, 2:0})

        self.assertEqualGetResponseJson('/vote/testapp/comment/2/clear/',
            {"score": {"score": -1, "num_votes": 2}, "success": True}, client=assistant_client)
        self.assertEqual(s_data,{1:1, 2:-1})

        self.assertEqualGetResponseJson('/vote/testapp/comment/2/clear/',
            {"score": {"score": 0, "num_votes": 2}, "success": True})
        self.assertEqual(s_data,{1:1, 2:-1})