from django.test import TestCase

from dynamics.forms import DynamicForm, MoleculeForm


class DynamicFormTest(TestCase):
    def test_has_fields(self):
        ''' Form must have 2 fields
        '''
        form = DynamicForm()
        try:
            self.assertCountEqual(['email', 'box_size'], form.fields)
        except AssertionError:
            # assertIemsEqual is no longer supported in Python 3.2+
            self.assertItemsEqual(['email', 'box_size'], form.fields)


class MoleculeFormTest(TestCase):
    def test_has_fields(self):
        ''' Form must have 1 fields
        '''
        form = MoleculeForm()
        try:
            self.assertCountEqual(['file'], form.fields)
        except AssertionError:
            # assertIemsEqual is no longer supported in Python 3.2+
            self.assertItemsEqual(['file'], form.fields)
