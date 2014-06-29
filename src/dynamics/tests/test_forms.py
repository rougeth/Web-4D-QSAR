from django.test import TestCase
from django.test.client import Client

from dynamics.forms import DynamicForm, MoleculeForm


class DynamicFormTest(TestCase):
    def test_dynamic_form_fields(self):
        ''' Form must have 2 fields
        '''
        form = DynamicForm()
        try:
            self.assertCountEqual(['email', 'box_size'], form.fields)
        except AssertionError:
            # assertIemsEqual is no longer supported in Python 3.2+
            self.assertItemsEqual(['email', 'box_size'], form.fields)

    def test_valid_form(self):
        ''' Form must be valid
        '''
        data = {
            'email': 'marco@rougeth.com',
            'box_size': 10,
        }

        form = DynamicForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        ''' Form must be invalid
        '''
        data = {}

        form = DynamicForm(data)
        self.assertFalse(form.is_valid())


class MoleculeFormTest(TestCase):

    def test_molecule_form_fields(self):
        ''' Form must have 1 fields
        '''
        form = MoleculeForm()
        try:
            self.assertCountEqual(['file'], form.fields)
        except AssertionError:
            # assertIemsEqual is no longer supported in Python 3.2+
            self.assertItemsEqual(['file'], form.fields)

    def test_invalid_form(self):
        ''' Form must be invalid
        '''
        data = {}
        form = MoleculeForm(data)

        self.assertFalse(form.is_valid())

