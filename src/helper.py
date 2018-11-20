from typing import List, Union

from src.datamodel import Pair, Expression, Nil, Number, NilType
from src.scheme_exceptions import OperandDeduceError, MathError, CallableResolutionError


def pair_to_list(pos: Pair) -> List[Expression]:
    out = []
    while pos is not Nil:
        if not isinstance(pos, Pair):
            raise OperandDeduceError(f"List terminated with '{pos}', not nil")
        out.append(pos.first)
        pos = pos.rest
    return out


def assert_all_numbers(operands):
    for operand in operands:
        if not isinstance(operand, Number):
            raise MathError(f"Unable to perform arithmetic, as {operand} is not a number.")


def verify_exact_callable_length(operator: Expression, expected: int, actual: int):
    if expected != actual:
        raise CallableResolutionError(f"{operator} expected {expected} operands, received {actual}.")


def verify_min_callable_length(operator: Expression, expected: int, actual: int):
    if expected > actual:
        raise CallableResolutionError(f"{operator} expected at least {expected} operands, received {actual}.")


def make_list(exprs: List[Expression], last: Expression = Nil) -> Union[Pair, NilType]:
    if len(exprs) == 0:
        return last
    return Pair(exprs[0], make_list(exprs[1:], last))
