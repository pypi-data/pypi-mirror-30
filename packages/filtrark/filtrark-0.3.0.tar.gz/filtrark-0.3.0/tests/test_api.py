import unittest
import filtrark

from unittest.mock import Mock


class TestApi(unittest.TestCase):

    def setUp(self):
        self.domain = [('field', '=', 5), ('field2', '=', 4)]
        self.mock_object = Mock(field=5, field2=4)

    def test_api_string(self):
        result = filtrark.string(self.domain)
        expected = 'field = 5 AND field2 = 4'
        self.assertEqual(result, expected)

    def test_api_expression(self):
        function = filtrark.expression(self.domain)

        def expected(obj):
            return obj.field == 5 and obj.field2 == 4

        self.assertEqual(function(self.mock_object),
                         expected(self.mock_object))

    def test_api_sql(self):
        result = filtrark.sql(self.domain)
        expected = ('field = %s AND field2 = %s', (5, 4))
        self.assertEqual(result, expected)
