from django.test import TestCase
from django.core.urlresolvers import reverse


# Create your tests here.
class HomeTest(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('home'))

    def test_get(self):
        ''' GET / must return status code 200
        '''
        self.assertEqual(200, self.response.status_code)

    def test_used_template(self):
        ''' GET / must use template core/home.html
        '''
        self.assertTemplateUsed(self.response, 'core/home.html')

class HowItWorksTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/how-it-works')

    def test_get(self):
        ''' GET /how-it-works must return status code 200
        '''
        self.assertEqual(200, self.response.status_code)

    def test_used_template(self):
        ''' GET /how-it-works must use template core/how_it_works.html
        '''
        self.assertTemplateUsed(self.response, 'core/how_it_works.html')

class DocumentationTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/doc')

    def test_get(self):
        ''' GET /docs must return status code 302 because it is a redirect view
        '''
        self.assertEqual(302, self.response.status_code)

class LicenseTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/license')

    def test_get(self):
        ''' GET /license must return status code 200
        '''
        self.assertEqual(200, self.response.status_code)

    def test_used_template(self):
        ''' GET /license must use template core/license.html
        '''
        self.assertTemplateUsed(self.response, 'core/license.html')
