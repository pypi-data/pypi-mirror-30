import ast


class PrettyPrintingVisitor(object):
    def __init__(self):
        super(PrettyPrintingVisitor, self).__init__()
        self.indentation_level = 0

    def indent(self):
        self.indentation_level += 4

    def dedent(self):
        self.indentation_level = max(self.indentation_level - 4, 0)

    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        return self.visit(item)
            elif isinstance(value, ast.AST):
                return self.visit(value)

    def line(self, line):
        return self.indentation_level * ' ' + line

    def parens(self, expr):
        return '(' + expr + ')'

    # Literals

    def visit_Num(self, node: ast.Num):
        return str(node.n)

    def visit_Str(self, node: ast.Str):
        return repr(node.s)

    def visit_List(self, node: ast.List):
        return '[' + ', '.join(self.visit(element) for element in node.elts) + ']'

    def visit_Tuple(self, node: ast.List):
        if len(node.elts) == 1:
            return '(' + self.visit(node.elts[0]) + ',' + ')'
        else:
            return '(' + ', '.join(self.visit(element) for element in node.elts) + ')'

    def visit_Set(self, node: ast.Set):
        return '{' + ', '.join(self.visit(element) for element in node.elts) + '}'

    def visit_Dict(self, node: ast.Dict):
        return '{' + ', '.join(self.visit(key) + ': ' + self.visit(value) if key is not None else '**' + value
                               for key, value in zip(node.keys, node.values)) + '}'

    def visit_Ellipsis(self, node: ast.Ellipsis):
        return '...'

    def visit_NameConstant(self, node: ast.NameConstant):
        if node.value is True:
            return 'True'
        elif node.value is False:
            return 'False'
        elif node.value is None:
            return 'None'

    # Expressions

    def visit_Name(self, node: ast.Name):
        return node.id

    def visit_Starred(self, node: ast.Starred):
        return "*" + self.visit(node.value)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return '+' + self.parens(self.visit(node.operand))
        elif isinstance(node.op, ast.USub):
            return '-' + self.parens(self.visit(node.operand))
        elif isinstance(node.op, ast.Not):
            return 'not ' + self.parens(self.visit(node.operand))
        elif isinstance(node.op, ast.Invert):
            return '~' + self.parens(self.visit(node.operand))

    def visit_BinOp(self, node: ast.BinOp):
        lhs = self.parens(self.visit(node.left))
        rhs = self.parens(self.visit(node.right))
        op = self.repr_binop(node.op)
        return ' '.join([lhs, op, rhs])

    def repr_binop(self, op):
        if isinstance(op, ast.Add):
            op = '+'
        elif isinstance(op, ast.Sub):
            op = '-'
        elif isinstance(op, ast.Mult):
            op = '*'
        elif isinstance(op, ast.Div):
            op = '/'
        elif isinstance(op, ast.FloorDiv):
            op = '//'
        elif isinstance(op, ast.Mod):
            op = '%'
        elif isinstance(op, ast.Pow):
            op = '**'
        elif isinstance(op, ast.LShift):
            op = '<<'
        elif isinstance(op, ast.RShift):
            op = '>>'
        elif isinstance(op, ast.BitOr):
            op = '|'
        elif isinstance(op, ast.BitXor):
            op = '^'
        elif isinstance(op, ast.BitAnd):
            op = '&'
        elif isinstance(op, ast.MatMult):
            op = '@'
        else:
            raise ValueError("Unknown operator: %r" % op)
        return op

    def visit_BoolOp(self, node: ast.BoolOp):
        if isinstance(node.op, ast.And):
            op = 'and'
        elif isinstance(node.op, ast.Or):
            op = 'or'
        else:
            raise ValueError("Unknown operator: %r" % node.op)
        return (' ' + op + ' ').join([self.parens(self.visit(value)) for value in node.values])

    def visit_Compare(self, node: ast.Compare):
        ops = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: 'is',
            ast.IsNot: 'is not',
            ast.In: 'in',
            ast.NotIn: 'not in',
        }
        first = self.parens(self.visit(node.left))
        rest = [
            item
            for comp, operand in zip(node.ops, node.comparators)
            for item in [ops.get(comp.__class__), self.parens(self.visit(operand))]
        ]
        return ' '.join([first] + rest)

    def visit_Call(self, node: ast.Call):
        func_expr = self.parens(self.visit(node.func))
        args = []
        args.extend(self.visit(arg) for arg in node.args)
        if hasattr(node, 'starargs') and node.starargs:
            args.append('*' + self.visit(node.starargs))
        for kw in node.keywords:
            if kw.arg is None:
                args.append('**' + self.visit(kw.value))
            else:
                args.append(kw.arg + '=' + self.visit(kw.value))
        if hasattr(node, 'kwargs') and node.kwargs:
            args.append('**' + self.visit(node.kwargs))
        csargs = ', '.join(args)
        return func_expr + '(' + csargs + ')'

    def visit_IfExp(self, node: ast.IfExp):
        return ' '.join([self.visit(node.body), 'if', self.visit(node.test), 'else', self.visit(node.orelse)])

    def visit_Attribute(self, node: ast.Attribute):
        return self.visit(node.value) + '.' + node.attr

    def visit_Index(self, slice: ast.Index):
        return self.visit(slice.value)

    def visit_Slice(self, slice: ast.Slice):
        sl = ''
        sl += self.visit(slice.lower) if slice.lower else ''
        sl += ':'
        sl += self.visit(slice.upper) if slice.upper else ''
        if slice.step:
            sl += ':'
            if isinstance(slice.step, ast.Name) and slice.step.id == 'None':
                pass
            else:
                sl += self.visit(slice.step) if slice.step else ''
        return sl

    def visit_ExtSlice(self, slice: ast.ExtSlice):
        return ', '.join(self.visit(sl) for sl in slice.dims)

    def visit_Subscript(self, node: ast.Subscript):
        slice = self.visit(node.slice)
        return self.visit(node.value) + '[' + slice + ']'

    def visit_comprehension(self, node: ast.comprehension):
        items = ['for', self.visit(node.target), 'in', self.visit(node.iter)]
        for item in node.ifs:
            items.extend(['if', self.visit(item)])
        return ' '.join(items)

    def visit_ListComp(self, node: ast.ListComp):
        elt = self.visit(node.elt)
        gens = ' '.join(self.visit(gen) for gen in node.generators)
        return '[' + elt + ' ' + gens + ']'

    def visit_SetComp(self, node: ast.SetComp):
        elt = self.visit(node.elt)
        gens = ' '.join(self.visit(gen) for gen in node.generators)
        return '{' + elt + ' ' + gens + '}'

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        elt = self.visit(node.elt)
        gens = ' '.join(self.visit(gen) for gen in node.generators)
        return elt + ' ' + gens

    def visit_DictComp(self, node: ast.DictComp):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = ' '.join(self.visit(gen) for gen in node.generators)
        return '{' + key + ': ' + value + ' ' + gens + '}'

    # Statements

    def visit_Expr(self, node: ast.Expr):
        return self.line(self.visit(node.value))

    def visit_Assign(self, node: ast.Assign):
        lhs = ", ".join(str(self.visit(target)) for target in node.targets)
        rhs = str(self.visit(node.value))
        return self.line(lhs + " = " + rhs)

    # TODO: AnnAssign

    def visit_AugAssign(self, node: ast.AugAssign):
        parts = [self.visit(node.target), self.repr_binop(node.op) + '=', self.visit(node.value)]
        return self.line(' '.join(parts))

    # TODO: print?

    def visit_Raise(self, node: ast.Raise):
        items = ['raise', self.visit(node.exc)]
        if node.cause:
            items.extend(['from', self.visit(node.cause)])
        return self.line(' '.join(items))

    def visit_Assert(self, node: ast.Assert):
        items = ['assert', self.visit(node.test)]
        if node.msg:
            items[-1] += ','
            items.append(self.visit(node.msg))
        return self.line(' '.join(items))

    def visit_Delete(self, node: ast.Delete):
        targets = ',  '.join(self.visit(target) for target in node.targets)
        return self.line('del ' + targets)

    def visit_Pass(self, node: ast.Pass):
        return self.line('pass')

    def visit_Import(self, node: ast.Import):
        aliases = []
        for alias in node.names:
            name = alias.name
            if alias.asname is not None:
                name += ' as ' + alias.asname
            aliases.append(name)
        return self.line('import ' + ', '.join(aliases))

    def visit_ImportFrom(self, node: ast.Import):
        modname = '.' * node.level + node.module
        parts = ['from', modname, 'import']
        comps = []
        for alias in node.names:
            name = alias.name
            if alias.asname is not None:
                name += ' as ' + alias.asname
            comps.append(name)
        parts.append(', '.join(comps))
        return self.line(' '.join(parts))

    def visit_If(self, node: ast.If):
        if_line = self.line(' '.join(['if', self.visit(node.test) + ':']))
        self.indent()
        then_lines = [self.visit(stmt) for stmt in node.body]
        self.dedent()
        print(repr(if_line), repr(then_lines))
        return '\n'.join([if_line] + then_lines)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        print("fundef", node.name)
        return self.generic_visit(node)

    def visit_Module(self, node: ast.Module):
        blocks = []
        for stmt in node.body:
            blocks.append(self.visit(stmt))

        return "\n".join(self.line(str(b)) for b in blocks)


def prettyprint(tree):
    visitor = PrettyPrintingVisitor()
    source = visitor.visit(tree)
    return source


source = """
'''yo yo yo'''
x = 3
y = (1, 2)
z = [1, 2]
zz = {"a": 1, "b": 2}
...
zzz = True, False, None
*x = 12
x = -5, +4, not True, ~False
x = 3 + 5 - 10 & 10
x and 1 or 40
1 < 2 < 3 <= 4
1 in [1,2,3]
foo(a, b, c, foo=bar)
foo(1, 2, *args, foo=bar, **kwargs)
5 if True else 1
foo.bar
x[1]
x[1:2]
x[1:2:3]
x[:2]
x[1:]
x[::3]
x[:]
x[1,2:3]
[x for x in xs]
[x for xs in xss for x in xs]
[x for x in xs if x > 0 if x % 2 == 0]
{x for x in xs}
(x for x in xs)
{x: y for x, y in xys}
x += 10
raise Exception("foo")
raise foo from bar
assert foo == bar
assert foo, bar

import foo
import foo as bar, baz
from foo import bar as baz, doo, yo as yoyo

if foo:
    if bar:
        baz
    yoyo
yoyoyo
"""
tree = ast.parse(source)
print(ast.dump(tree))
print("="*80)
print(prettyprint(tree))
print("="*80)
