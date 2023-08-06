import ast
import logging

from python_agent.common import constants
from python_agent.common.constants import AST_ARGUMENTS_EMPTY_VALUES

log = logging.getLogger(__name__)


def iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    and all items of fields that are lists of nodes.
    """
    for name, field in ast.iter_fields(node):
        if isinstance(field, ast.AST):
            setattr(field, "parent", node)
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, ast.AST):
                    setattr(item, "parent", node)
                    yield item


def walk(node):
    """
    Recursively yield all descendant nodes in the tree starting at *node*
    (including *node* itself), in no specified order.  This is useful if you
    only want to modify nodes in place and don't care about the context.
    """
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def set_node_id(node, tree, rel_path):
    if node == tree:
        # we are at the root level. sl_id is the filename
        setattr(node, "sl_id", rel_path)
    else:
        # we concat the parent sl_id with our name
        parent = getattr(node, "parent", None)
        parent_id = getattr(parent, "sl_id", "")
        node_name = str(getattr(node, "name", ""))
        setattr(node, "sl_id", parent_id + "@" + node_name)


def get_last_node(node):
    last_node = node
    body = getattr(node, "body", None)
    if body:
        if isinstance(body, list):
            last_node = node.body[-1] if node.body else node
        else:
            last_node = node.body
    max_lineno = node.lineno
    for child in ast.walk(last_node):
        if getattr(child, "lineno", -1) > max_lineno:
            last_node = child
            max_lineno = child.lineno
    return last_node


def clean_functiondef_body(node):
    if hasattr(node, "name"):
        node.name = ""
    if hasattr(node, "args"):
        node.args = clean_args(node)
    if hasattr(node, "body"):
        node.body = []
    if hasattr(node, "decorator_list"):
        node.decorator_list = []
    if hasattr(node, "returns"):
        node.returns = None


def clean_lambda_body(node):
    if hasattr(node, "name"):
        node.name = ""
    if hasattr(node, "args"):
        node.args = clean_args(node)
    if hasattr(node, "body"):
        node.body = []


def clean_args(node):
    kwargs = {}
    for field in ast.arguments._fields:
        if field in AST_ARGUMENTS_EMPTY_VALUES:
            kwargs[field] = AST_ARGUMENTS_EMPTY_VALUES.get(field)
    return ast.arguments(**kwargs)


def parse(source, filename='<unknown>', mode='exec', flags=ast.PyCF_ONLY_AST):
    """
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
    """
    try:
        return compile(source, filename, mode, flags)
    except SyntaxError as e:
        around_source = source.split("\n")
        start = max(0, e.lineno - 4)
        end = min(len(around_source) - 1, e.lineno + 4)
        msg = "Failed parsing source code into ast. source=%s. args=%s" % ("\n".join(around_source[start:end]), e.args)
        log.exception(msg)
        raise Exception(msg)
