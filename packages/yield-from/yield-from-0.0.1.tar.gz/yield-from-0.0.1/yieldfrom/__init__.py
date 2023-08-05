"""
Backport of the `yield from` functionality in Python 3. Please carefully read
the docstring of `rewrite_yield_from` for details.
"""
import ast
import sys

from asttools import quoted_template, get_ast


def yield_from(expression):
    """For use exclusively with the `rewrite_yield_from` decorator."""
    pass  # Calls to this function are replaced with the _yield_from template below.


def rewrite_yield_from(fn):
    """
    Forgive me padre for I have sinned.

    Rewrite the AST of the given function, replacing instances of `yield_from`
    usage with the semantic equivalent specified in
    https://www.python.org/dev/peps/pep-0380/#formal-semantics .

    N.B. that expressions must _exactly_ match the form `{NAME} = yield_from({EXPR})`
    or `yield_from({EXPR})` -- `imported_module.yield_from({EXPR})`, e.g., will not
    work.

    Decorated functions must not use any of the following names for their
    variables: _e, _i, _m, _r, _s, _y, _x, & _result .
    """
    fn_ast = get_ast(fn)

    # Replace yield_from calls in function AST
    rewritten_ast = _YieldFromExprReplacer().visit(
        _YieldFromAssignReplacer().visit(
            fn_ast
        )
    )
    ast.fix_missing_locations(rewritten_ast)

    # Recompile rewritten AST into function object and return
    env = sys._getframe(1).f_locals.copy()
    env[rewrite_yield_from.__name__] = lambda x: x
    rewritten_fn = compile(
        ast.Module(body=[rewritten_ast]),
        getattr(fn.__module__, '__file__', '<no_module>'),
        'exec'
    )
    exec(rewritten_fn, fn.__globals__, env)
    return env[fn.__name__]


class _YieldFromAssignReplacer(ast.NodeTransformer):
    """
    Replace expressions of the form `{NAME} = yield_from({EXPR})` with the
    semantic equivalent of `{NAME} = yield from {EXPR}`, as specified in
    PEP-0380.
    """
    def visit_Assign(self, node):
        try:
            value_call_func_name = node.value.func.id
        except AttributeError:
            return self.generic_visit(node)
        if value_call_func_name != yield_from.__name__:
            return self.generic_visit(node)

        replacement_nodes = _yield_from(
            node.targets[0],  # The name being assigned to. Does not support multiple assignment, i.e. x = y = yield_from(z).
            node.value.args[0]  # The expression being passed as the first (only) argument to yield_from.
        )

        # In order to replace the assignment with multiple nodes, we wrap them in an "if 1:" block.
        return ast.If(
            test=ast.Num(n=1),
            body=replacement_nodes,
            orelse=[]
        )


class _YieldFromExprReplacer(ast.NodeTransformer):
    """
    Replace expressions of the form `yield_from({EXPR})` with the semantic
    equivalent of `yield from {EXPR}` specified in PEP-0380.

    Transformation must be applied only after replacing expressions of the form
    `{NAME} = yield_from({EXPR})`.
    """
    def visit_Expr(self, node):
        if not isinstance(node.value, ast.Call):
            return self.generic_visit(node)
        try:
            value_call_func_name = node.value.func.id
        except AttributeError:
            return self.generic_visit(node)
        if value_call_func_name != yield_from.__name__:
            return self.generic_visit(node)

        replacement_nodes = _yield_from(
            ast.Name(id='_result'),  # A throwaway name
            node.value.args[0]  # The expression being passed as the first argument to yield_from.
        )

        return ast.If(
            test=ast.Num(n=1),
            body=replacement_nodes,
            orelse=[]
        )


@quoted_template
def _yield_from(result, expr):  # adapted from PEP-380
    _i = iter(expr)
    _r = None
    _y = None
    try:
        _y = next(_i)
    except StopIteration as _e:
        if hasattr(_e, 'value'):  # hasattr checks are added to ease 2/3 iterator API inconsistency
            _r = _e.value
        else:
            _r = _y
    else:
        while 1:
            try:
                _s = yield _y
            except GeneratorExit as _e:
                try:
                    _m = _i.close
                except AttributeError:
                    pass
                else:
                    _m()
                raise _e
            except BaseException as _e:
                _x = sys.exc_info()
                try:
                    _m = _i.throw
                except AttributeError:
                    raise _e
                else:
                    try:
                        _y = _m(*_x)
                    except StopIteration as _e:
                        if hasattr(_e, 'value'):
                            _r = _e.value
                        else:
                            _r = _y
                        break
            else:
                try:
                    if _s is None:
                        _y = next(_i)
                    else:
                        _y = _i.send(_s)
                except StopIteration as _e:
                    if hasattr(_e, 'value'):
                        _r = _e.value
                    else:
                        _r = _y
                    break
    result = _r
