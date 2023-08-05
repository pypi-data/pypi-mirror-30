import unittest

from filtrark.sql_parser import SqlParser


class TestSqlParser(unittest.TestCase):

    def setUp(self):
        self.parser = SqlParser()

    def test_sql_parser_object_creation(self):
        self.assertTrue(isinstance(self.parser, SqlParser))

    def test_sql_parser_parse_tuple(self):
        filter_tuple = ('field', '=', 99)
        expected = ('field = %s', 99)
        result = self.parser._parse_term(filter_tuple)
        self.assertEqual(result, expected)

    def test_sql_parser_parse_single_term(self):
        domain = [('field', '=', 7)]
        expected = ('field = %s', (7,))
        result = self.parser.parse(domain)
        self.assertEqual(result, expected)

    def test_sql_parser_default_join(self):
        stack = ['field2 <> %s', 'field = %s']
        expected = 'field = %s AND field2 <> %s'
        result = self.parser._default_join(stack)
        self.assertEqual(result, [expected])

    def test_string_parser_parse_multiple_terms(self):
        test_domains = [
            ([('field', '=', 7), ('field2', '!=', 8)],
             ('field = %s AND field2 <> %s', (7, 8))),
            ([('field', '=', 7), ('field2', '!=', 8), ('field3', '>=', 9)],
             ('field = %s AND field2 <> %s AND field3 >= %s', (7, 8, 9))),
            (['|', ('field', '=', 7), ('field2', '!=', 8),
              ('field3', '>=', 9)],
                ('field = %s OR field2 <> %s AND field3 >= %s', (7, 8, 9))),
            (['|', ('field', '=', 7),
              '!', ('field2', '!=', 8), ('field3', '>=', 9)],
             ('field = %s OR NOT field2 <> %s AND field3 >= %s', (7, 8, 9))),
            (['!', ('field', '=', 7)], ('NOT field = %s', (7,))),
        ]

        for test_domain in test_domains:
            result = self.parser.parse(test_domain[0])
            expected = test_domain[1]
            self.assertEqual(result, expected)

    def test_sql_parser_with_empty_list(self):
        domain = []
        result = self.parser.parse(domain)
        expected = "TRUE", ()
        self.assertEqual(result, expected)

    def test_sql_parser_with_lists_of_lists(self):
        domain = [['field', '=', 7], ['field2', '!=', 8]]
        expected = ('field = %s AND field2 <> %s', (7, 8))
        result = self.parser.parse(domain)
        self.assertEqual(result, expected)
