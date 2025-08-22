#!/usr/bin/env python3
"""Detect orphan modules by scanning project imports."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent / "src"


def module_name(path: Path) -> str:
    rel = path.relative_to(PROJECT_ROOT).with_suffix("")
    return ".".join(rel.parts)


def collect_modules() -> Dict[str, Path]:
    modules: Dict[str, Path] = {}
    for file in PROJECT_ROOT.rglob("*.py"):
        modules[module_name(file)] = file
    return modules


def collect_imports() -> Set[str]:
    imported: Set[str] = set()
    for file in PROJECT_ROOT.rglob("*.py"):
        name = module_name(file)
        with file.open("r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(file))
            except SyntaxError:
                continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                base_parts = name.split(".")[:-node.level] if node.level else []
                if node.module:
                    base_parts += node.module.split(".")
                base = ".".join(base_parts)
                for alias in node.names:
                    target = f"{base}.{alias.name}" if alias.name != "*" else base
                    imported.add(target)
    return imported


def main() -> None:
    modules = collect_modules()
    imports = collect_imports()
    orphans = [m for m in modules if m not in imports]
    if orphans:
        print("Orphan modules:")
        for mod in sorted(orphans):
            print(f"- {mod} ({modules[mod]})")
    else:
        print("No orphan modules found.")


if __name__ == "__main__":
    main()
