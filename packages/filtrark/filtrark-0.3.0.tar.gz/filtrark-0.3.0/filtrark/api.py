from typing import List, Union, Tuple, Callable, Any
from .string_parser import StringParser
from .expression_parser import ExpressionParser
from .sql_parser import SqlParser
from .type_definitions import TermTuple


def string(domain: List[Union[str, TermTuple]]) -> str:
    parser = StringParser()
    return parser.parse(domain)


def expression(domain: List[Union[str, TermTuple]]) -> Callable:
    parser = ExpressionParser()
    return parser.parse(domain)


def sql(domain: List[Union[str, TermTuple]]) -> Tuple[Any, Any]:
    parser = SqlParser()
    return parser.parse(domain)
