from base import BaseTestCase
from test_project.testapp.models import Book, Shelf

class BaseFieldsTestCase(BaseTestCase):
    def assertGetCheckData(self, url, data, client=None):
        if client is None:
            client = self.client

        self.assertEqual(client.get(url).status_code,200)
        self.assertEqual(data, self.check_data())

class FieldsTestBook(BaseFieldsTestCase):
    def setUp(self):
        super(FieldsTestBook,self).setUp()
        Book.objects.create(name="Alice's Adventures in Wonderland", slug='alice')
        Book.objects.create(name="Pillow Problems", slug='pillow')
        Book.objects.create(name="Sylvie and Bruno", slug="bruno")

    def check_data(self):
        return dict(Book.objects.all().values_list('slug','total_voting_score'))

    def test_single_user(self):
        self.assertEqual(self.check_data(), {u'alice': 0, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/comment/1/up/', {u'alice': 0, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/1/up/', {u'alice': 1, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/1/down/', {u'alice': -1, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/1/down/', {u'alice': -1, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/2/up/', {u'alice': -1, u'bruno': 0, u'pillow': 1})

    def test_with_assistant(self):
        assistant_client = self.get_assistant_client()

        self.assertGetCheckData('/vote/testapp/book/1/up/', {u'alice': 1, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/1/up/',
            {u'alice': 2, u'bruno': 0, u'pillow': 0}, client=assistant_client)

        self.assertGetCheckData('/vote/testapp/book/1/down/', {u'alice': 0, u'bruno': 0, u'pillow': 0})

        self.assertGetCheckData('/vote/testapp/book/2/up/',
            {u'alice': 0, u'bruno': 0, u'pillow': 1}, client=assistant_client)

        self.assertGetCheckData('/vote/testapp/book/3/up/',
            {u'alice': 0, u'bruno': 1, u'pillow': 1}, client=assistant_client)

        self.assertGetCheckData('/vote/testapp/book/3/up/', {u'alice': 0, u'bruno': 2, u'pillow': 1})

class FieldsTestShelf(BaseFieldsTestCase):
    def setUp(self):
        super(FieldsTestShelf,self).setUp()
        Shelf.objects.create(num=1)
        Shelf.objects.create(num=2)
        Shelf.objects.create(num=3)

    def check_data(self):
        ret = {}
        for item in Shelf.objects.values('num', 'tvc', 'tvs'):
            ret[item.pop('num')] = item

        return ret



    def test_vote(self):
        self.assertEqual(self.check_data(), {
            1: {'tvc': 0, 'tvs': 0},
            2: {'tvc': 0, 'tvs': 0},
            3: {'tvc': 0, 'tvs': 0}
        })

        self.assertGetCheckData('/vote/testapp/shelf/1/up/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 0, 'tvs': 0},
            3: {'tvc': 0, 'tvs': 0}
        })

        self.assertGetCheckData('/vote/testapp/shelf/1/up/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 0, 'tvs': 0},
            3: {'tvc': 0, 'tvs': 0}
        })

        self.assertGetCheckData('/vote/testapp/shelf/2/up/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 1, 'tvs': 1},
            3: {'tvc': 0, 'tvs': 0}
        })

        self.assertGetCheckData('/vote/testapp/shelf/3/down/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 1, 'tvs': 1},
            3: {'tvc': 1, 'tvs': -1}
        })

        assistant_client = self.get_assistant_client()

        self.assertGetCheckData('/vote/testapp/shelf/3/down/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 1, 'tvs': 1},
            3: {'tvc': 2, 'tvs': -2}
        }, client=assistant_client)

        self.assertGetCheckData('/vote/testapp/shelf/2/down/', {
            1: {'tvc': 1, 'tvs': 1},
            2: {'tvc': 2, 'tvs': 0},
            3: {'tvc': 2, 'tvs': -2}
        }, client=assistant_client)

        self.assertGetCheckData('/vote/testapp/shelf/1/up/', {
            1: {'tvc': 2, 'tvs': 2},
            2: {'tvc': 2, 'tvs': 0},
            3: {'tvc': 2, 'tvs': -2}
        }, client=assistant_client)