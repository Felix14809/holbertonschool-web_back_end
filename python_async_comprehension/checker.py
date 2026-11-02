#!/usr/bin/env python3
"""Local pre-checker for Holberton Python async projects.
 
Checks each Python file for: shebang, executable bit, trailing newline,
pycodestyle, type annotations (3.8-compatible), and docstrings.
 
Usage:
    ./check.py              # check *.py in the current folder (skips *main*)
    ./check.py 0-foo.py ... # check specific files
    ./check.py --all        # include *main* files too
 
This only approximates the real checker: it can't see the hidden tests,
the exact docstring length rule, or the checker's Python version.
"""
import ast
import glob
import os
import shutil
import subprocess
import sys
 
SHEBANG = "#!/usr/bin/env python3"
MIN_DOC_WORDS = 4          # guess: real checker's length rule is unknown
PEP585 = {"list", "dict", "tuple", "set", "frozenset", "type"}
 
RED, GREEN, YELLOW, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[0m"
if not sys.stdout.isatty():
    RED = GREEN = YELLOW = RESET = ""
 
 
def check_basics(path, text, problems):
    """Check shebang, executable bit and trailing newline."""
    first = text.split("\n", 1)[0]
    if first != SHEBANG:
        problems.append("line 1 must be exactly '{}' (got {!r})"
                        .format(SHEBANG, first))
    if not os.access(path, os.X_OK):
        problems.append("not executable (run: chmod +x {})".format(path))
    if not text.endswith("\n"):
        problems.append("file doesn't end with a newline")
    elif text.endswith("\n\n"):
        problems.append("file ends with blank line(s) (W391)")
 
 
def check_pycodestyle(path, problems, warnings):
    """Run pycodestyle on the file if it is installed."""
    cmd = shutil.which("pycodestyle")
    if not cmd:
        warnings.append("pycodestyle not installed, style not checked "
                        "(sudo apt install pycodestyle)")
        return
    out = subprocess.run([cmd, path], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, universal_newlines=True)
    for line in out.stdout.splitlines():
        problems.append("pycodestyle: " + line.split(":", 1)[-1])
 
 
def doc_ok(doc):
    """Return True if a docstring looks like a real sentence."""
    return doc is not None and len(doc.split()) >= MIN_DOC_WORDS
 
 
def check_docs(tree, problems):
    """Check module, class and function docstrings."""
    if not doc_ok(ast.get_docstring(tree)):
        problems.append("module docstring missing or too short")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            if not doc_ok(ast.get_docstring(node)):
                problems.append("line {}: '{}' docstring missing or too "
                                "short".format(node.lineno, node.name))
 
 
def bad_annotation(ann):
    """Return a reason if an annotation won't work on Python 3.8."""
    if ann is None:
        return None
    for node in ast.walk(ann):
        if (isinstance(node, ast.Subscript) and
                isinstance(node.value, ast.Name) and
                node.value.id in PEP585):
            return "'{}[...]' needs 3.9+, use typing.{}".format(
                node.value.id, node.value.id.capitalize()
                if node.value.id != "frozenset" else "FrozenSet")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return "'X | Y' needs 3.10+, use typing.Union / Optional"
    return None
 
 
def check_annotations(tree, problems):
    """Check every function and coroutine is fully type-annotated."""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        where = "line {}: '{}'".format(node.lineno, node.name)
        args = node.args
        all_args = (getattr(args, "posonlyargs", []) + args.args +
                    args.kwonlyargs)
        for a in all_args:
            if a.arg in ("self", "cls"):
                continue
            if a.annotation is None:
                problems.append("{} param '{}' not annotated"
                                .format(where, a.arg))
        for a in (args.vararg, args.kwarg):
            if a is not None and a.annotation is None:
                problems.append("{} param '{}' not annotated"
                                .format(where, a.arg))
        if node.returns is None:
            problems.append("{} missing return annotation (-> ...)"
                            .format(where))
        anns = [a.annotation for a in all_args] + [node.returns]
        anns += [a.annotation for a in (args.vararg, args.kwarg) if a]
        for ann in anns:
            reason = bad_annotation(ann)
            if reason:
                problems.append("{} {}".format(where, reason))
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            reason = bad_annotation(node.annotation)
            if reason:
                problems.append("line {}: {}".format(node.lineno, reason))
 
 
def check_file(path):
    """Run all checks on one file and print the result."""
    problems, warnings = [], []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    check_basics(path, text, problems)
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as e:
        problems.append("syntax error line {}: {}".format(e.lineno, e.msg))
        tree = None
    if tree is not None:
        try:
            ast.parse(text, feature_version=(3, 8))
        except SyntaxError as e:
            problems.append("line {}: syntax not valid on Python 3.8 ({})"
                            .format(e.lineno, e.msg))
        check_docs(tree, problems)
        check_annotations(tree, problems)
    check_pycodestyle(path, problems, warnings)
 
    status = (RED + "FAIL" if problems else GREEN + "OK  ") + RESET
    print("{} {}  ({} lines)".format(status, path, text.count("\n")))
    for p in problems:
        print("     - " + p)
    for w in warnings:
        print("     " + YELLOW + "! " + w + RESET)
    return not problems
 
 
def main():
    """Pick the files to check, check them, and set the exit code."""
    args = [a for a in sys.argv[1:] if a != "--all"]
    files = args or sorted(glob.glob("*.py"))
    if not args and "--all" not in sys.argv:
        files = [f for f in files if "main" not in f and
                 f != os.path.basename(__file__)]
    if not files:
        print("No .py files to check.")
        sys.exit(1)
    if not os.path.isfile("README.md"):
        print(YELLOW + "! no README.md in this folder" + RESET)
    results = [check_file(f) for f in files]
    print("\n{}/{} files passed".format(sum(results), len(results)))
    sys.exit(0 if all(results) else 1)
 
 
if __name__ == "__main__":
    main()