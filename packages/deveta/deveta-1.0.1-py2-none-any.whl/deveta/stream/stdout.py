"""This module is for methods that print to the stdout stream. Currently,
the main purpose is to print text with a non-default foreground color. The colors supported
are the eight basic ASNI terminal colors: 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', and 'white'.
"""
from __future__ import print_function
from ansi_colors import FG_COLORS
__all__ = ['kprint', 'rprint', 'gprint', 'yprint', 'bprint', 'mprint', 'cprint', 'wprint']


"""Explaination of ANSI_ESC_SEQ syntac:
    \\x := the following two characters are hex-digits
    1b hex-digits := the escape control character
    [ := Control Sequence Introducer
Extra resources:
    https://en.wikipedia.org/wiki/ANSI_escape_code
    http://wiki.bash-hackers.org/scripting/terminalcodes
"""
_ANSI_ESC_SEQ = "\x1b[{}m"


class InvalidForegroundColorError(Exception):
    """Raised within `_format_fg_color` when invalid color specified"""
    pass


def _format_fg_color(target, color):
    """Purpose:
        Format `target` object using ansi `color` from `ansi_colors.FG_COLORS`.
    Parameters:
        `target`:
            instance type: any object such that the __str__ method is defined
        `color`:
            instance type: any object such that the __hash__ method is defined
            values: FG_COLORS.keys()
    Raise:
        `InvalidForegroundColorError`:
            if color is not in FG_COLORS
        *plus built-in exceptions if they occur
    Return:
        String object
    """
    suffix = _ANSI_ESC_SEQ.format(39)  # 39 will reset the foreground color to default
    if color in FG_COLORS:
        prefix = _ANSI_ESC_SEQ.format(FG_COLORS[color])
    else:
        raise InvalidForegroundColorError
    return '{}{}{}'.format(prefix, target, suffix)


def _color_args(*args, **kwargs):
    """Purpose:
        reformat arguments that will be printed so that they are the
        desired ANSI color.
    Parameters:
        `args`:
            instance type: any object such that the __str__ method is defined
        `kwargs`:
            `fg_color`:
                instance type: string
                values: FG_COLORS.keys()
    Raise:
        `InvalidForegroundColorError`:
            This propagates from `_color_args`.
        *plus built-in exceptions if they occur
    Returns:
        list of strings which are wrapped with ANSI escapes
    """
    return [_format_fg_color(arg, kwargs['fg_color']) for arg in args]


def _ansi_print(*args, **kwargs):
    """Purpose:
        Print ansi foreground colored text using `future_print`. It accepts the same arguments
        and keyword-arguments as `future_print`, plus the additional keyword-argument `fg_color`.
    Parameters:
        Extra parameters besides those defined for `future_print`.
        `fg_color`:
            instance type: string
            values: FG_COLORS.keys()
    Raise:
        `InvalidForegroundColorError`:
            This propagates from `_color_args`.
        *plus built-in exceptions if they occur
    """
    fg_color = kwargs.pop('fg_color')
    args = _color_args(*args, fg_color=fg_color)
    print(*args, **kwargs)


def kprint(*args, **kwargs):
    """Purpose:
        The first letter of the method name maps to a color below.
            r -> Red
            g -> Green
            y -> Yellow
            b -> Blue
            m -> Magenta
            c -> Cyan
            w -> White
            k -> blacK
        It follows that kprint prints black, rprint prints red, and so on. Black is mapped to k
        considering that black is a common default, where blue is mapped to b in anticipation of the
        user's disposition while using this module --- printing text with a non-default foreground color.
    Parameters:
        Accepts the same arguments and keyword-arguments as future_print
    Raise:
        `InvalidForegroundColorError`:
            This propagates from `_color_args`.
        *plus built-in exceptions if they occur
    """
    kwargs.update({'fg_color': 'black'})
    _ansi_print(*args, **kwargs)


def rprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'red'})
    _ansi_print(*args, **kwargs)


def gprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'green'})
    _ansi_print(*args, **kwargs)


def yprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'yellow'})
    _ansi_print(*args, **kwargs)


def bprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'blue'})
    _ansi_print(*args, **kwargs)


def mprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'magenta'})
    _ansi_print(*args, **kwargs)


def cprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'cyan'})
    _ansi_print(*args, **kwargs)


def wprint(*args, **kwargs):
    """see docstring under kprint"""
    kwargs.update({'fg_color': 'white'})
    _ansi_print(*args, **kwargs)
