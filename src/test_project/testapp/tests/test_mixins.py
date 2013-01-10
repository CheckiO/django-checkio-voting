import json

class TestRequestJsonMixIn(object):
    def assertEqualJson(self,first, second, message=None):
        if isinstance(first, basestring):
            first = json.loads(first)

        if isinstance(second, basestring):
            second = json.loads(second)

        return self.assertEqual(first, second, message)

    def assertEqualGetResponseJson(self,url, data, status=200, client=None, message=''):
        if client is None:
            client = self.client

        resp = client.get(url)
        self.assertEqual(resp.status_code, status, 'Status. '+message)
        self.assertEqualJson(resp.content, data, 'Data. '+message)
