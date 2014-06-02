from django.test import TestCase


class NewDynamicTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/new-dynamic')

    def test_get(self):
        ''' GET /dynamic must return status code 200
        '''
        self.assertEqual(200, self.response.status_code)

    def test_used_template(self):
        ''' GET /dynamic must use dynamic/new_dynamic.html
        '''
        self.assertTemplateUsed(self.response, 'dynamics/new_dynamic.html')

    def test_csrf(self):
        ''' Check if csrf tag exists in the html
        '''
        self.assertContains(self.response, 'csrfmiddlewaretoken')
