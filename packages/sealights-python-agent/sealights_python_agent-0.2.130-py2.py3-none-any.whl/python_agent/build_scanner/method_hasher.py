import ast
import hashlib

from python_agent.build_scanner import ast_utils
from python_agent.build_scanner.entities.v3.method_data import MethodMetaData, MethodData

from python_agent.packages import astunparse


class MethodHasher(object):

    def __init__(self, method_cleaner_visitor_class):
        self.method_cleaner_visitor_class = method_cleaner_visitor_class

    def calculate_method_hash(self, node):
        code = astunparse.unparse(node)
        copied_node = ast_utils.parse(code)
        if isinstance(node, ast.FunctionDef):
            copied_node = copied_node.body[0]
        if isinstance(node, ast.Lambda):
            copied_node = copied_node.body[0].value

        self.method_cleaner_visitor_class().visit(copied_node)

        return self.calculate_hash(copied_node)

    def calculate_hash(self, node):
        m = hashlib.md5()
        m.update(astunparse.unparse(node).encode("utf-8"))
        return m.hexdigest()

    def _is_parameterless_method(self, args):
        if not args or not args.args:
            return True
        return False

    def _calculate_method_sig_hash(self, node):
        args = getattr(node, "args", None)
        if self._is_parameterless_method(args):
            return ""
        params_string = ",".join(map(astunparse.unparse, args.args))
        m = hashlib.md5()
        m.update(params_string.encode("utf-8"))
        return m.hexdigest()

    def _calculate_method_position(self, node):
        lineno = node.lineno
        col_offset = node.col_offset
        if hasattr(node, "decorator_list") and node.decorator_list:
            lineno = node.decorator_list[-1].lineno + 1
            col_offset = min(node.decorator_list[-1].col_offset - 1, 0)
        return lineno, col_offset

    def build_method(self, physical_path, name, node):
        method_hash = self.calculate_method_hash(node)
        last_node = ast_utils.get_last_node(node)
        last_node_lineno = last_node.lineno
        last_node_col_offset = last_node.col_offset + len(astunparse.unparse(last_node).strip("\n"))
        lineno, col_offset = self._calculate_method_position(node)
        position = [lineno, col_offset]
        end_position = [last_node_lineno, last_node_col_offset]
        sig_hash = self._calculate_method_sig_hash(node)

        method_type = None
        is_anonymous = isinstance(node, ast.Lambda)
        if is_anonymous:
            method_type = "lambda"
        if name == "__init__":
            method_type = "constructor"
        unique_id = "%(source)s@%(lineno)s,%(col_offset)s" % {
            "source": physical_path, "lineno": node.lineno, "col_offset": node.col_offset
        }

        meta = MethodMetaData(method_type, is_anonymous)
        method = MethodData(unique_id, name, position, end_position, meta, method_hash, sig_hash)
        return method
