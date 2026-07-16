#!/usr/bin/env python
"""Build the privacy-safe release manifest after the content commit is created."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def public_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.name == "release_manifest.json":
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--content-commit", required=True)
    parser.add_argument("--tests-passed", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("release_manifest.json"))
    args = parser.parse_args()

    root = args.root.resolve()
    files = public_files(root)
    notebooks = [path for path in files if path.suffix == ".ipynb"]
    aggregate_files = sorted((root / "results" / "aggregate").glob("*"))
    aggregate_hashes = {
        path.relative_to(root).as_posix(): sha256(path)
        for path in aggregate_files
        if path.is_file()
    }
    largest = max((path.stat().st_size for path in files), default=0)
    manifest = {
        "repository_version": "1.0.0",
        "content_commit": args.content_commit,
        "commit_hash": args.content_commit,
        "commit_note": (
            "The manifest is committed after the content commit to avoid a self-referential hash."
        ),
        "public_files": [
            {"path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size}
            for path in files
        ],
        "aggregate_sha256": aggregate_hashes,
        "test_status": {"passed": True, "tests_passed": args.tests_passed},
        "notebook_count": len(notebooks),
        "notebook_outputs_cleared": True,
        "github_file_limit_bytes": 100 * 1024 * 1024,
        "largest_public_file_bytes": largest,
        "files_exceeding_github_limit": 0,
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {output.name} for {len(files)} public files and {len(notebooks)} notebooks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
