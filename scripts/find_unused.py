#!/usr/bin/env python3
"""Scan project imports to detect orphan modules.

The script parses all Python files under ``src`` and compares the list of
available modules to those imported somewhere else. Modules that are never
imported are printed to stdout. This helps spotting dead code that can be
archived or removed.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Set


def _iter_python_files(root: Path) -> Set[Path]:
    return {p for p in root.rglob("*.py") if p.is_file()}


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def collect_modules(root: Path) -> Set[str]:
    return { _module_name(root, p) for p in _iter_python_files(root) }


def collect_imports(root: Path) -> Set[str]:
    imports: Set[str] = set()
    for path in _iter_python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
    return imports


def find_orphans(root: Path) -> Set[str]:
    modules = collect_modules(root)
    imports = collect_imports(root)
    orphans = set()
    for module in modules:
        if module.endswith(".__init__"):
            continue
        if not any(i == module or i.startswith(module + ".") for i in imports):
            orphans.add(module)
    return orphans


def main() -> None:
    root = Path("src")
    orphans = sorted(find_orphans(root))
    for name in orphans:
        print(name)


if __name__ == "__main__":
    main()
