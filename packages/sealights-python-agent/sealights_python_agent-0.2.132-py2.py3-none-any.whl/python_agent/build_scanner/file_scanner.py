"""
    file_scanner module is part of the build scan process.
    For a given full python file path and its relative path:
        - Parse the code to ast
        - Traverse the tree
        - Calculate method hash for functions and lambdas
        - Calculate file hash
"""
import logging
import traceback

from python_agent.build_scanner import ast_utils
from python_agent.build_scanner.entities.v3.file_data import FileData
from python_agent.build_scanner.method_hasher import MethodHasher
from python_agent.build_scanner.visitors import SealightsVisitor, MethodCleanerVisitor

log = logging.getLogger(__name__)


class FileScanner(object):

    def calculate_file_signature(self, full_path, rel_path):
        result = FileData(rel_path)
        try:
            with open(full_path, 'r') as f:
                code = f.read()
            tree = ast_utils.parse(code)
            method_hasher = MethodHasher(MethodCleanerVisitor)
            SealightsVisitor(result, method_hasher).visit(tree)
            result.hash = method_hasher.calculate_hash(ast_utils.parse(code))
        except SyntaxError as e:
            result.error = traceback.format_exc()
            log.error("File ignored due to syntax error. %s. problematic code: (%s)" % (full_path, e.text.strip()))
        except Exception as e:
            result.error = traceback.format_exc()
            log.error("Failed creating mapping for file. Ignoring... %s" % full_path)
        return result
