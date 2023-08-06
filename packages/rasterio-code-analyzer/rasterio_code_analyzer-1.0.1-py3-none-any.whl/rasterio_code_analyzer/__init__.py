import ast
from collections import defaultdict
import sys


def is_w_mode_open_call(node):
    """Return True if node represents `rasterio.open(path, "w", ...)`"""

    return isinstance(
        node.func, ast.Attribute
    ) and node.func.attr == "open" and isinstance(node.func.value, ast.Name) and node.func.value.id == "rasterio" and len(
        node.args
    ) > 1 and isinstance(node.args[1], ast.Str) and node.args[
        1
    ].s == "w"


class RasterioNodeVisitor(ast.NodeVisitor):
    """Analyze code for reads of Rasterio datasets opened in 'w' mode
    """

    def __init__(self):
        super().__init__()
        self.context = [("global", {})]
        self.dings = []

    def visit_FunctionDef(self, node):
        self.context.append(("function", {}))
        self.generic_visit(node)
        self.context.pop()

    def visit_ClassDef(self, node):
        self.context.append(("class", {}))
        self.generic_visit(node)
        self.context.pop()

    def visit_Lambda(self, node):
        self.context.append(("function", {}))
        self.generic_visit(node)
        self.context.pop()

    def visit_Call(self, node):

        if is_w_mode_open_call(node):

            if isinstance(node.parent, ast.withitem):
                name = node.parent.optional_vars
                key = getattr(name, 'id', None)
                self.context[-1][1][key] = name

            elif isinstance(node.parent, ast.Assign):
                name = node.parent.targets[0]
                self.context[-1][1][name.id] = name

        elif isinstance(node.func, ast.Attribute) and (node.func.attr == "read" or node.func.attr == "read_masks"):

            if isinstance(node.func.value, ast.Call) and is_w_mode_open_call(
                node.func.value
            ):
                self.dings.append((None, node))

            elif isinstance(node.func.value, ast.Name):
                if node.func.value.id in self.context[-1][1]:
                    self.dings.append((node.func.value.id, node))

        self.generic_visit(node)


class Reporter(object):

    def __init__(self):
        self.tree = None
        self.visitor = RasterioNodeVisitor()

    def analyze(self, code):
        self.tree = add_parents(ast.parse(code))
        self.visitor.visit(self.tree)

    def report(self):
        return [{"name": name, "node": node} for name, node in self.visitor.dings]


def add_parents(tree):
    """For every node in the tree add a reference to its parent"""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


def main():
    """Reporting script"""

    with open(sys.argv[1]) as f:
        code = f.read()

    finder = Reporter()
    finder.analyze(code)

    for record in finder.report():
        print(f"In file {sys.argv[1]} {record['name']}.read() is called on line {record['node'].lineno} and column {record['node'].col_offset} where {record['name']} is opened in 'w' mode")
