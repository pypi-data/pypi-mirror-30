# -*- coding: utf-8 -*-
import ast
import inspect
import sys


try:
    from flake8.engine import pep8 as stdin_utils
except ImportError:
    from flake8 import utils as stdin_utils


WHITE_LIST = [
    '__name__',
    '__doc__',
    'credits',
]


if sys.version_info >= (3, 0):
    import builtins
    BUILTINS = [
        a[0]
        for a in inspect.getmembers(builtins)
        if a[0] not in WHITE_LIST
    ]
else:
    import __builtin__
    BUILTINS = [
        a[0]
        for a in inspect.getmembers(__builtin__)
        if a[0] not in WHITE_LIST
    ]


class BuiltinsChecker(object):
    name = 'flake8_builtins'
    version = '1.2.1'
    assign_msg = 'A001 "{0}" is a python builtin and is being shadowed, ' \
                 'consider renaming the variable'
    argument_msg = 'A002 "{0}" is used as an argument and thus shadows a ' \
                   'python builtin, consider renaming the argument'
    class_attribute_msg = 'A003 "{0}" is a python builtin, consider ' \
                          'renaming the class attribute'

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        tree = self.tree

        if self.filename == 'stdin':
            lines = stdin_utils.stdin_get_value()
            tree = ast.parse(lines)

        for statement in ast.walk(tree):
            for child in ast.iter_child_nodes(statement):
                child.__flake8_builtins_parent = statement

        function_nodes = [ast.FunctionDef]
        if getattr(ast, 'AsyncFunctionDef', None):
            function_nodes.append(ast.AsyncFunctionDef)
        function_nodes = tuple(function_nodes)

        for_nodes = [ast.For]
        if getattr(ast, 'AsyncFor', None):
            for_nodes.append(ast.AsyncFor)
        for_nodes = tuple(for_nodes)

        with_nodes = [ast.With]
        if getattr(ast, 'AsyncWith', None):
            with_nodes.append(ast.AsyncWith)
        with_nodes = tuple(with_nodes)

        for statement in ast.walk(tree):
            value = None
            if isinstance(statement, ast.Assign):
                value = self.check_assignment(statement)

            elif isinstance(statement, function_nodes):
                value = self.check_function_definition(statement)

            elif isinstance(statement, for_nodes):
                value = self.check_for_loop(statement)

            elif isinstance(statement, with_nodes):
                value = self.check_with(statement)

            elif isinstance(statement, ast.excepthandler):
                value = self.check_exception(statement)

            elif isinstance(statement, ast.ListComp):
                value = self.check_list_comprehension(statement)

            elif isinstance(statement, (ast.Import, ast.ImportFrom)):
                value = self.check_import(statement)

            elif isinstance(statement, ast.ClassDef):
                value = self.check_class(statement)

            if value:
                for line, offset, msg, rtype in value:
                    yield line, offset, msg, rtype

    def check_assignment(self, statement):
        is_class_def = False
        if type(statement.__flake8_builtins_parent) is ast.ClassDef:
            is_class_def = True

        for element in statement.targets:
            if isinstance(element, ast.Name) and \
                    element.id in BUILTINS:

                line = element.lineno
                offset = element.col_offset
                if is_class_def:
                    msg = self.class_attribute_msg
                else:
                    msg = self.assign_msg
                yield (
                    line,
                    offset,
                    msg.format(element.id),
                    type(self),
                )

    def check_function_definition(self, statement):
        if statement.name in BUILTINS:
            yield (
                statement.lineno,
                statement.col_offset,
                self.argument_msg.format(statement.name),
                type(self),
            )

        if sys.version_info >= (3, 0):
            for arg in statement.args.args:
                if isinstance(arg, ast.arg) and \
                        arg.arg in BUILTINS:

                    line = arg.lineno
                    offset = arg.col_offset
                    yield (
                        line,
                        offset,
                        self.argument_msg.format(arg.arg),
                        type(self),
                    )
        else:
            for arg in statement.args.args:
                if isinstance(arg, ast.Name) and \
                        arg.id in BUILTINS:

                    line = arg.lineno
                    offset = arg.col_offset
                    yield (
                        line,
                        offset,
                        self.argument_msg.format(arg.id),
                        type(self),
                    )

    def check_for_loop(self, statement):
        stack = [statement.target]
        while stack:
            item = stack.pop()
            if isinstance(item, ast.Tuple):
                stack.extend(list(item.elts))
            else:
                if item.id in BUILTINS:
                    yield (
                        statement.lineno,
                        statement.col_offset,
                        self.assign_msg.format(item.id),
                        type(self),
                    )

    def check_with(self, statement):
        if getattr(statement, 'optional_vars', None):
            var = statement.optional_vars
            if var.id in BUILTINS:
                yield (
                    statement.lineno,
                    statement.col_offset,
                    self.assign_msg.format(var.id),
                    type(self),
                )
        if getattr(statement, 'items', None):
            for item in statement.items:
                var = item.optional_vars
                if var and var.id in BUILTINS:
                    yield (
                        statement.lineno,
                        statement.col_offset,
                        self.assign_msg.format(var.id),
                        type(self),
                    )

    def check_exception(self, statement):
        exception_name = statement.name
        value = ''
        if isinstance(exception_name, ast.Name):
            value = exception_name.id
        elif isinstance(exception_name, str):  # Python +3.x
            value = exception_name

        if value in BUILTINS:
            yield (
                statement.lineno,
                statement.col_offset,
                self.assign_msg.format(value),
                type(self),
            )

    def check_list_comprehension(self, statement):
        for generator in statement.generators:
            if isinstance(generator.target, ast.Name) \
                    and generator.target.id in BUILTINS:
                yield (
                    statement.lineno,
                    statement.col_offset,
                    self.assign_msg.format(generator.target.id),
                    type(self),
                )
            elif isinstance(generator.target, ast.Tuple):
                for tuple_element in generator.target.elts:
                    if tuple_element.id in BUILTINS:
                        yield (
                            statement.lineno,
                            statement.col_offset,
                            self.assign_msg.format(tuple_element.id),
                            type(self),
                        )

    def check_import(self, statement):
        for name in statement.names:
            if name.asname in BUILTINS:
                yield (
                    statement.lineno,
                    statement.col_offset,
                    self.assign_msg.format(name.asname),
                    type(self),
                )

    def check_class(self, statement):
        if statement.name in BUILTINS:
            yield (
                statement.lineno,
                statement.col_offset,
                self.assign_msg.format(statement.name),
                type(self),
            )
