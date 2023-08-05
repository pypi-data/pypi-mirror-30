from typing import List, Union, Tuple, Any
from .type_definitions import TermTuple


class SqlParser:

    def __init__(self) -> None:
        self.comparison_dict = {
            '=': lambda x, y:  ' = '.join([str(x), str(y)]),
            '!=': lambda x, y: ' <> '.join([str(x), str(y)]),
            '<=': lambda x, y: ' <= '.join([str(x), str(y)]),
            '<': lambda x, y: ' < '.join([str(x), str(y)]),
            '>': lambda x, y: ' > '.join([str(x), str(y)]),
            '>=': lambda x, y: ' >= '.join([str(x), str(y)]),
            'in': lambda x, y: ' in '.join([str(x), str(y)])
        }

        self.binary_dict = {
            '&': lambda a, b: a + ' AND ' + b,
            '|': lambda a, b: a + ' OR ' + b}

        self.unary_dict = {
            '!': lambda a: 'NOT ' + a}

        self.default_join_operator = '&'

    def parse(self, domain: List[Union[str, TermTuple]]) -> Tuple[Any, Any]:
        if not domain:
            return "TRUE", ()
        stack = []  # type: List[str]
        params = []
        for item in list(reversed(domain)):
            if isinstance(item, str) and item in self.binary_dict:
                first_operand = stack.pop()
                second_operand = stack.pop()
                string_term = str(
                    self.binary_dict[str(item)](
                        first_operand, second_operand))
                stack.append(string_term)
            elif isinstance(item, str) and item in self.unary_dict:
                operand = stack.pop()
                stack.append(
                    str(self.unary_dict[str(item)](
                        operand)))

            stack = self._default_join(stack)

            if isinstance(item, (list, tuple)):
                result_tuple = self._parse_term(item)
                stack.append(result_tuple[0])
                params.append(result_tuple[1])

        result_query = str(self._default_join(stack)[0])
        return result_query, tuple(reversed(params))

    def _default_join(self, stack: List[str]) -> List[str]:
        operator = self.default_join_operator
        if len(stack) == 2:
            first_operand = stack.pop()
            second_operand = stack.pop()
            value = str(self.binary_dict[operator](
                str(first_operand), str(second_operand)))
            stack.append(value)
        return stack

    def _parse_term(self, term_tuple: TermTuple) -> Tuple[str, Any]:
        field, operator, value = term_tuple
        function = self.comparison_dict.get(operator)
        placeholder = '%s'
        result = (function(field, placeholder), value)
        return result
