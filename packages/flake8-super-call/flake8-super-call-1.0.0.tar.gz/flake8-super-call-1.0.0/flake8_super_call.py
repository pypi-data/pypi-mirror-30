"""Flake8 extension that checks for bad super calls.
"""

import ast

__version__ = '1.0.0'


def _is_super_function_call(node):
    return isinstance(node.func, ast.Name) and node.func.id == 'super'


def _are_super_arguments_bad(args):
    return (len(args) == 2 and isinstance(args[0], ast.Attribute) and
            isinstance(args[0].value, ast.Name) and args[0].value.id == 'self'
            and args[0].attr == '__class__')


class Checker(ast.NodeVisitor):
    name = 'flake8_super_call'
    version = __version__

    message = 'S777 Cannot use {} as first argument of {} call'.format(
        'self.__class__', 'super()')

    def __init__(self, tree):
        self.tree = tree
        self.errors = []

    def visit_Call(self, node):
        self.generic_visit(node)
        if _is_super_function_call(node):
            if _are_super_arguments_bad(node.args):
                self.errors.append(
                    (node.lineno, node.col_offset, self.message, type(self))
                )

    def run(self):
        self.visit(self.tree)
        for lineno, col_offset, message, ctype in self.errors:
            yield lineno, col_offset, message, ctype
