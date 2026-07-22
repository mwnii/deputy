#!/usr/bin/env python3
"""
Lint Runner — runs ruff + pyright and returns results.

Usage:
    python tools/lint.py <file>        # Lint a single file
    python tools/lint.py --check       # Lint all Python files in project
    python tools/lint.py --format      # Auto-format all Python files
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def lint_file(filepath: str) -> dict:
    """Run ruff check, ruff format, and pyright on a single file."""
    results = {
        "file": filepath,
        "ruff_check": None,
        "ruff_format": None,
        "pyright": None,
        "passed": True,
    }

    # Ruff check
    try:
        ruff = subprocess.run(
            ["ruff", "check", filepath],
            capture_output=True,
            text=True,
        )
        results["ruff_check"] = {
            "returncode": ruff.returncode,
            "output": ruff.stdout.strip(),
        }
        if ruff.returncode != 0:
            results["passed"] = False
    except FileNotFoundError:
        results["ruff_check"] = {"returncode": -1, "output": "ruff not installed"}

    # Ruff format check
    try:
        fmt = subprocess.run(
            ["ruff", "format", "--check", filepath],
            capture_output=True,
            text=True,
        )
        results["ruff_format"] = {
            "returncode": fmt.returncode,
            "output": fmt.stdout.strip(),
        }
    except FileNotFoundError:
        results["ruff_format"] = {"returncode": -1, "output": "ruff not installed"}

    # Pyright (if available)
    try:
        pyright = subprocess.run(
            ["pyright", filepath],
            capture_output=True,
            text=True,
        )
        results["pyright"] = {
            "returncode": pyright.returncode,
            "output": pyright.stdout.strip(),
        }
        if pyright.returncode != 0:
            results["passed"] = False
    except FileNotFoundError:
        results["pyright"] = {"returncode": -1, "output": "pyright not installed"}

    return results


def check_project() -> dict:
    """Lint all Python files in the project."""
    root = Path(__file__).parent.parent
    py_files = list(root.rglob("*.py"))
    # Skip venv, __pycache__, .venv
    py_files = [
        f for f in py_files
        if ".venv" not in str(f)
        and "venv" not in str(f)
        and "__pycache__" not in str(f)
        and "node_modules" not in str(f)
    ]

    results = {"total_files": len(py_files), "passed": 0, "failed": 0, "errors": []}

    for f in py_files:
        result = lint_file(str(f))
        if result["passed"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "file": str(f),
                "ruff": result["ruff_check"]["output"] if result["ruff_check"] else "",
                "pyright": result["pyright"]["output"] if result["pyright"] else "",
            })

    return results


def format_project() -> None:
    """Auto-format all Python files."""
    root = Path(__file__).parent.parent
    subprocess.run(["ruff", "format", str(root)], check=False)
    subprocess.run(["ruff", "check", "--fix", str(root)], check=False)
    print("Formatted all Python files.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/lint.py <file> | --check | --format")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--check":
        results = check_project()
        print(f"\nLint Results: {results['passed']}/{results['total_files']} passed")
        if results["failed"] > 0:
            print(f"\n{results['failed']} files failed:")
            for err in results["errors"]:
                print(f"\n  {err['file']}:")
                if err["ruff"]:
                    print(f"    ruff: {err['ruff'][:200]}")
                if err["pyright"]:
                    print(f"    pyright: {err['pyright'][:200]}")
            sys.exit(1)
        else:
            print("All files passed!")

    elif arg == "--format":
        format_project()

    else:
        result = lint_file(arg)
        status = "PASSED" if result["passed"] else "FAILED"
        print(f"\nLint {status}: {result['file']}")

        if result["ruff_check"] and result["ruff_check"]["returncode"] != 0:
            print(f"\nruff check:\n{result['ruff_check']['output']}")

        if result["ruff_format"] and result["ruff_format"]["returncode"] != 0:
            print(f"\nruff format (needs formatting):\n{result['ruff_format']['output']}")

        if result["pyright"] and result["pyright"]["returncode"] != 0:
            print(f"\npyright:\n{result['pyright']['output']}")

        if not result["passed"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
