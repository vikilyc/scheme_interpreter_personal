import math
import re
from typing import List

import log
from css_colors import COLORS
from datamodel import Expression, Number, Undefined, String, Symbol
from environment import global_attr
from evaluate_apply import Frame
from helper import verify_exact_callable_length, verify_min_callable_length
from primitives import SingleOperandPrimitive, BuiltIn
from scheme_exceptions import OperandDeduceError, IrreversibleOperationError

ABSOLUTE_MOVE = "M"
RELATIVE_MOVE = "m"
ABSOLUTE_LINE = "L"
RELATIVE_LINE = "l"
COMPLETE_PATH = "Z"


def make_action(command: str, *params: float) -> str:
    return command + " " + " ".join(str(param) for param in params)


def graphics_fragile(func):
    def out(*args, **kwargs):
        if log.logger.fragile:
            raise IrreversibleOperationError()
        return func(*args, **kwargs)
    return out


class Move:
    def __init__(self, stroke, fill, thickness):
        self.stroke = stroke
        self.fill = fill
        self.thickness = thickness
        self.seq = []

    def export(self):
        return {
            "seq": " ".join(self.seq),
            "stroke": self.stroke,
            "fill": self.fill,
        }


class Canvas:
    SIZE = 1000

    def __init__(self):
        self.x = None
        self.y = None
        self.angle = None
        self.bg_color = None
        self.moves: List[Move] = None
        self.pen_down = None
        self.size = None

        self.reset()

    @graphics_fragile
    def set_color(self, color):
        self.moves.append(self.new_move())
        self.moves[-1].stroke = color

    @graphics_fragile
    def move(self, x: float, y: float):
        if self.pen_down:
            self.moves[-1].seq.append(make_action(ABSOLUTE_LINE, x, y))
        else:
            self.moves[-1].seq.append(make_action(ABSOLUTE_MOVE, x, y))
        self.x = x
        self.y = y

    @graphics_fragile
    def set_bg(self, color):
        self.bg_color = color

    @graphics_fragile
    def rotate(self, theta: float):
        self.angle -= theta
        self.angle %= 360

    @graphics_fragile
    def abs_rotate(self, theta: float):
        self.angle = -theta % 360

    @graphics_fragile
    def forward(self, dist: float):
        self.move(self.x + dist * math.cos(self.angle / 360 * 2 * math.pi),
                  self.y + dist * math.sin(self.angle / 360 * 2 * math.pi))

    @graphics_fragile
    def pendown(self):
        self.pen_down = True

    @graphics_fragile
    def penup(self):
        self.pen_down = False

    @graphics_fragile
    def rect(self, x: float, y: float, color: str):
        raise NotImplementedError()

    def export(self):
        path = [move.export() for move in self.moves]
        return {
            "path": path,
            "bgColor": self.bg_color,
        }

    @graphics_fragile
    def reset(self):
        self.x = 0
        self.y = 0
        self.angle = -90
        self.bg_color = "#ffffff"
        self.moves = [self.new_move()]
        self.pen_down = True
        self.size = 1

    @graphics_fragile
    def new_move(self) -> Move:
        out = Move("black", "transparent", 1)
        out.seq.append(make_action(ABSOLUTE_MOVE, self.x, self.y))
        return out


def make_color(expression: Expression) -> str:
    if not isinstance(expression, String) and not isinstance(expression, Symbol):
        raise OperandDeduceError(f"Expected a String or Symbol, received {expression}.")
    color = expression.value.lower()
    # regex from https://stackoverflow.com/questions/30241375/python-how-to-check-if-string-is-a-hex-color-code
    if color not in COLORS and not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
        raise OperandDeduceError(f"Expected a valid CSS or hex color code, received {expression}.")
    return color


@global_attr("backward")
@global_attr("back")
@global_attr("bk")
class Backward(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().forward(-operand.value)
        return Undefined


@global_attr("begin_fill")
class BeginFill(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        raise NotImplementedError("fill not yet implemented")


@global_attr("bgcolor")
class BGColor(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        log.logger.get_canvas().set_bg(make_color(operand))
        return Undefined


@global_attr("circle")
class Circle(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 1, len(operands))
        if len(operands) > 2:
            verify_exact_callable_length(self, 2, len(operands))
        raise NotImplementedError("circle not yet implemented")


@global_attr("clear")
class Clear(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        log.logger.get_canvas().reset()
        return Undefined


@global_attr("color")
class Color(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        log.logger.get_canvas().set_color(make_color(operand))
        return Undefined


@global_attr("end_fill")
class EndFill(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        raise NotImplementedError("fill not yet implemented")


@global_attr("forward")
@global_attr("fd")
class Forward(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().forward(operand.value)
        return Undefined


@global_attr("left")
@global_attr("lt")
class Left(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().rotate(operand.value)
        return Undefined


@global_attr("pendown")
@global_attr("pd")
class PenDown(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        log.logger.get_canvas().pendown()
        return Undefined


@global_attr("penup")
@global_attr("pu")
class PenUp(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        log.logger.get_canvas().penup()
        return Undefined


@global_attr("pixel")
class Pixel(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 3, len(operands))
        x, y, c, = operands
        for v in x, y:
            if not isinstance(v, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {v}")
        log.logger.get_canvas().rect(x.value, y.value, make_color(c))
        return Undefined


@global_attr("pixelsize")
class PixelSize(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().size = operand.value
        return Undefined


@global_attr("rgb")
class RGB(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 3, len(operands))
        for operand in operands:
            if not isinstance(operand, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
            if not 0 <= operand.value <= 1:
                raise OperandDeduceError(f"RGB values must be between 0 and 1, not {operand}")
        return String("#" + "".join('{:02X}'.format(int(x.value * 255)) for x in operands))


@global_attr("right")
@global_attr("rt")
class Right(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().rotate(-operand.value)
        return Undefined


@global_attr("screen_width")
@global_attr("screen_height")
class ScreenSize(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        return Number(log.logger.get_canvas().SIZE)


@global_attr("setheading")
@global_attr("seth")
class SetHeading(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().abs_rotate(90 - operand.value)
        return Undefined


@global_attr("setposition")
@global_attr("setpos")
@global_attr("goto")
class SetPosition(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        for operand in operands:
            if not isinstance(operand, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        log.logger.get_canvas().move(operands[0].value, operands[1].value)
        return Undefined
