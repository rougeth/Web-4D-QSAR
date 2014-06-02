from django.test import TestCase

from dynamics.forms import DynamicForm


class DynamicFormTest(TestCase):
    def test_has_fields(self):
        ''' Form must have 4 fields
        '''
        form = DynamicForm()
        try:
            self.assertCountEqual(['email', 'box_size', 'file'], form.fields)
        except AssertionError:
            # assertIemsEqual is no longer supported in Python 3.2+
            self.assertItemsEqual(['email', 'box_size', 'file'], form.fields)
