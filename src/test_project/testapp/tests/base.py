from testapp.models import Comment
from django.contrib.auth.models import User
from django.test import TestCase, Client
from test_mixins import TestRequestJsonMixIn
from django.test.signals import setting_changed
from voting.models import Vote

def reload_settings(*args,**kwargs):
    #import ipdb; ipdb.set_trace();
    from voting import settings
    reload(settings)

setting_changed.connect(reload_settings)

class BaseTestCase(TestCase, TestRequestJsonMixIn):
    def setUp(self):
        author = User.objects.create_user('oduvan','alexander@lyabah.com','none')
        self.assertEqual(Comment.objects.create(
            author = author,
            text = 'tets com'
        ).pk, 1)
        self.assertFalse(Vote.objects.all().count())
        self.client.login(username='oduvan', password='none')

    def get_assistant_client(self):
        assistant = User.objects.create_user('assistant', 'assistant@gmail.com', 'none')
        assistant_client = Client()
        assistant_client.login(username='assistant', password='none')
        return assistant_client