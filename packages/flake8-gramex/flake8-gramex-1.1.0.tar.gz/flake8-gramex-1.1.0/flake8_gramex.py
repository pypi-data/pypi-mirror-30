'''Extension for flake8 that finds usage of open.'''
import ast
from collections import deque

__version__ = '1.1.0'


class CheckErrors(object):
    '''Check encoding, constants, etc'''
    name = 'flake8-gramex'
    version = __version__

    # We report these types of errors
    errors = {
        'E910': 'Specify encoding= for %s()',
        'E911': 'Use .format or %% if required instead of %s()',
        'E912': 'Define magic constant %s as a variable. Name it clearly',
    }

    # We ensure that encoding= is used in these functions
    open_functions = ['open', 'io.open', 'codecs.open', 'DB.open']
    encoding_functions = [
        'csv',                                          # DB.csv
        'read_csv', 'read_table', 'read_fwf',           # pd.*
        'read_html', 'read_sas', 'read_stata',          # pd.*
        'to_csv', 'to_stata', 'to_excel',               # pd.*
    ]

    def __init__(self, tree, filename):
        # Add ._parent attribute to every node
        self.tree = ParentNodeTransformer().visit(tree)

    def _error(self, node, msg, args):
        return (node.lineno, node.col_offset,
                '%s: %s' % (msg, self.errors[msg] % args), type(self))

    def check_encoding(self, node):
        '''Returns function name at node that ought to use encoding, else None'''
        # If **kwargs are used, there *might* be an encoding= in it, but we
        # can't detect it. Since this is usually used inside libraries,
        # and not used often, just ignore this scenario.
        if hasattr(node, 'kwargs') and node.kwargs:
            return None
        # In Python 3.5 or above, there's no kwargs. It uses keyword(arg=None)
        if any(keyword.arg is None for keyword in node.keywords):
            return None

        # Check if the encoding= kwarg has been used
        has_encoding = 'encoding' in {keyword.arg for keyword in node.keywords}

        # Get the full function name
        name = fname(node)

        # open() functions must have encodings
        if name in self.open_functions and not has_encoding:
            # but not for binary files, nor if there's a **kwargs
            if not _is_binary_mode(node):
                return name

        # Functions that support encoding should have an encoding
        func = name.split('.')[-1] if '.' in name else name
        if func in self.encoding_functions and not has_encoding:
            return name

    def check_str(self, node):
        '''Returns string function at node that is not used as a class, else None'''
        # Get the full function name
        name = fname(node)

        if name in ('str', 'unicode'):
            return name

    well_known_values = set(dict(
        half=0.5,
        months_in_a_year=12,
        hours_in_a_day=24,
        weeks_in_a_year=52,
        minutes_in_an_hour=60,
        seconds_in_an_hour=3600,
        seconds_in_a_day=86400,
        days_in_a_year=365,
        hundred=100,
        thousand=1000,
        kb=1024,
    ).values())

    def check_magic_number(self, node):
        '''Returns number if it is not a trivial number, else None'''
        if _is_being_assigned(node):
            return None

        n = node.n
        if n < 0:
            n = -n
        if type(n) is float:
            # Ignore well known values
            if n in self.well_known_values:
                return None
            # Report any (other) float with decimals
            if n % 1 != 0:
                return n
            # Report any floats beyond 10
            if n > 10:
                return n
        elif type(n) is int:
            # Report any ints beyond 10 other than a few well known ones
            if n > 10 and n not in self.well_known_values:
                return n

    def check_magic_str(self, node):
        '''Returns str if it is a hex color code, else None'''
        if _is_being_assigned(node):
            return None

        if node.s.startswith('#'):
            try:
                int(node.s[1:], base=16)
                return node.s
            except ValueError:
                pass

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                error_val = self.check_encoding(node)
                if error_val:
                    yield self._error(node, 'E910', error_val)
                error_val = self.check_str(node)
                if error_val:
                    yield self._error(node, 'E911', error_val)

            elif isinstance(node, ast.Num):
                error_val = self.check_magic_number(node)
                if error_val:
                    yield self._error(node, 'E912', error_val)

            elif isinstance(node, ast.Str):
                error_val = self.check_magic_str(node)
                if error_val:
                    yield self._error(node, 'E912', error_val)

# ----------------------------------------------------------------------------
# Utility functions


class ParentNodeTransformer(object):
    '''
    Adds a new field to every node:

    - _parent - link to parent node
    - _parents - list of all parents
    - _parent_field - name of field in parent node including child node
    - _parent_field_index - parent node field index, if it is a list

    astmonkey.transformers.ParentNodeTransformer
    https://github.com/konradhalas/astmonkey/blob/master/astmonkey/transformers.py

    Copy-pasting this instead of importing because pip install astmonkey fails
    in Python 3 due to a pydot dependency.

    TODO: This raises an error. See https://gitlab.com/pycqa/flake8/issues/127
    '''

    def visit(self, node):
        if not hasattr(node, '_parent'):
            node._parent = None
            node._parents = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        self.visit(item)
                        self._set_parnt_fields(item, node, field, index)
            elif isinstance(value, ast.AST):
                self.visit(value)
                self._set_parnt_fields(value, node, field)
        return node

    def _set_parnt_fields(self, node, parent, field, index=None):
        node._parent = parent
        node._parents.append(parent)
        node._parent_field = field
        node._parent_field_index = index


class FuncVisitor(ast.NodeVisitor):
    def __init__(self):
        self._name = deque()

    @property
    def name(self):
        return '.'.join(self._name)

    @name.deleter
    def name(self):
        self._name.clear()

    def visit_Name(self, node):             # noqa: function must be visit_Class (Capitalised)
        self._name.appendleft(node.id)

    def visit_Attribute(self, node):        # noqa: function must be visit_Class (Capitalised)
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)


def fname(node):
    '''Get function name from an AST node'''
    funcvisitor = FuncVisitor()
    funcvisitor.visit(node.func)
    return funcvisitor.name


def _is_binary_mode(node):
    '''Node is an open()-like function. Is it being opened in binary mode?'''
    # If mode is specifed as a keyword arg, e.g. open('file', mode='wb')
    for keyword in node.keywords:
        if keyword.arg == 'mode':
            return 'b' in keyword.value.s

    # If mode is specified as a positional arg, e.g. open('file', 'wb')
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Str):
        return 'b' in node.args[1].s

    return False


def _is_being_assigned(node):
    '''
    node is a number or a string. Is it being assigned to a variable? Treat
    these as assignments:

        a = 1
        a = (1, 2)
        a = [1, 2]
        {'a': 1}
        function(a=1)
        def function(a=1)
        def function(a=(1, 2))
        def function(a=[1, 2])
        dict.get(key, 1)
    '''
    if node._parent_field == 'value':
        # a = 1
        if isinstance(node._parent, ast.Assign):
            return True
        # function(a=1)
        if isinstance(node._parent, ast.keyword):
            return True

    elif node._parent_field == 'values':
        # {'a': 1}
        if isinstance(node._parent, ast.Dict):
            return True

    elif node._parent_field == 'elts':
        # a = (1,2)
        if isinstance(node._parent, (ast.Tuple, ast.List)):
            return _is_being_assigned(node._parent)

    elif node._parent_field == 'defaults':
        # def function(a=1)
        return True

    elif node._parent_field == 'args':
        # If the parameter is the 2nd argument:
        # Ignore .get(..., default) and .setdefault(..., default)
        if node._parent_field_index == 1:
            # x.get returns fname of 'x.get' but {}.get returns of 'get'
            # Standardise both ways
            method = fname(node._parent)
            if '.' in method:
                method = method.split('.')[-1]
            if method in ('get', 'setdefault'):
                return True
