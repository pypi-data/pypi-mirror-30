from unittest import TestCase

import qcodes as qc
import qcodes.utils.validators as vals


class BookkeepingValidator(vals.Validator):

    def __init__(self, min_value=-float("inf"), max_value=float("inf")):
        self.values_validated = []

    def validate(self, value, context=''):
        self.values_validated.append(value)

    is_numeric = True


class TestParameter(TestCase):

    def test_number_of_validations(self):

        p = qc.Parameter('p', set_cmd=None, initial_value=0,
                         vals=BookkeepingValidator())

        self.assertEqual(p.vals.values_validated, [0])

        p.step = 1
        p.set(10)

        self.assertEqual(p.vals.values_validated,
                         [0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9])
