"""Privacy-safe validation for aggregate artifacts and release structure."""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from pathlib import Path
from urllib.parse import unquote

AGGREGATE_SCHEMAS = {
    "internal_performance.csv": {
        "model",
        "cv_macro_auc_mean",
        "cv_macro_auc_sd",
        "heldout_macro_auc",
    },
    "delong_summary.csv": {
        "class",
        "comparison",
        "uncorrected_p",
        "bonferroni_p_9",
        "bh_p_9",
    },
    "external_stress_test.csv": {"branch", "scenario", "cases", "hcc_sensitivity"},
    "radiomics_imputation_controls.csv": {"condition", "hcc_sensitivity"},
    "c2_crop_retention.csv": {"metric", "count", "total", "percent"},
    "internal_sex_provenance.csv": {"metric", "count", "scope"},
    "internal_sex_sensitivity.csv": {"model", "scenario", "heldout_macro_auc"},
    "internal_per_class.csv": {"class", "support", "heldout_auc"},
    "internal_paired_tests.csv": {"comparison", "paired_t_pvalue", "wilcoxon_pvalue"},
    "external_adapter_qc.csv": {"metric", "group", "count", "total"},
}
_SENSITIVE_AGGREGATE_COLUMNS = {
    "patient_id",
    "case_id",
    "subject_id",
    "accession_number",
    "dicom_uid",
    "date_of_birth",
}

_SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}
_PATIENT_FILE_SUFFIXES = (
    ".dcm",
    ".dicom",
    ".nii",
    ".nii.gz",
    ".npz",
    ".parquet",
    ".pt",
    ".pth",
    ".ckpt",
    ".tar",
    ".zip",
    ".7z",
    ".docx",
    ".pdf",
)
_UNFINISHED_MARKERS = tuple(
    marker.lower()
    for marker in (
        "TO" + "DO",
        "FIX" + "ME",
        "T" + "BD",
        "T" + "BC",
        "Coming" + " soon",
        "Insert" + " link",
        "Add" + " later",
        "Example" + ".com",
        "Your" + " name",
        "Your" + " email",
        "Replace" + " this",
        "Tempo" + "rary",
        "Dr" + "aft",
        "Unti" + "tled",
        "Lorem" + " ipsum",
        "Dummy" + " result",
        "Fake" + " result",
        "Place" + "holder",
    )
)
_PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[/\\]" + "Users" + r"[/\\]", re.IGNORECASE),
    re.compile(r"/content/" + "drive", re.IGNORECASE),
    re.compile(r"/mnt/" + "data", re.IGNORECASE),
)
_MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_CREDENTIAL_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"gh[pousr]_[0-9A-Za-z]{30,}"),
    re.compile(r"sk-[0-9A-Za-z]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile("X-Amz-" + "Signature=", re.IGNORECASE),
)
_DEVELOPMENT_TRACE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        "Chat" + "GPT",
        "Open" + "AI",
        "Clau" + "de",
        "Co" + "pilot",
        "Gem" + "ini",
        "Co-authored" + "-by",
        "\\.co" + "dex",
        "AI-" + "generated",
        "AI " + "generated",
    )
)


def iter_release_files(root: Path):
    """Yield regular release files while excluding local tool and Git state."""

    for path in root.rglob("*"):
        if not path.is_file() or any(
            part in _SKIP_PARTS or part.endswith(".egg-info") for part in path.parts
        ):
            continue
        yield path


def validate_aggregate_directory(aggregate_dir: Path) -> list[str]:
    """Validate required aggregate schemas and the reproducibility JSON object."""

    issues: list[str] = []
    for filename, required_columns in AGGREGATE_SCHEMAS.items():
        path = aggregate_dir / filename
        if not path.is_file():
            issues.append(f"Missing aggregate artifact: {path.relative_to(aggregate_dir.parent)}")
            continue
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            columns = set(reader.fieldnames or ())
            rows = list(reader)
        missing = required_columns - columns
        if missing:
            issues.append(f"{filename} is missing columns: {sorted(missing)}")
        sensitive = columns & _SENSITIVE_AGGREGATE_COLUMNS
        if sensitive:
            issues.append(f"{filename} contains patient-level columns: {sorted(sensitive)}")
        if not rows:
            issues.append(f"{filename} has no aggregate rows")

    status_path = aggregate_dir / "reproducibility_status.json"
    if not status_path.is_file():
        issues.append("Missing aggregate artifact: aggregate/reproducibility_status.json")
    else:
        with status_path.open(encoding="utf-8") as stream:
            status = json.load(stream)
        if status.get("exact_end_to_end_reconstruction") is not False:
            issues.append("Reproducibility status must not claim exact end-to-end reconstruction")
        if status.get("patient_level_artifacts_public") is not False:
            issues.append("Reproducibility status must preserve the patient-data boundary")
    return issues


def notebook_output_issues(root: Path) -> list[str]:
    """Return notebooks containing outputs, execution counts, or excessive metadata."""

    issues: list[str] = []
    for path in root.rglob("*.ipynb"):
        with path.open(encoding="utf-8") as stream:
            notebook = json.load(stream)
        for index, cell in enumerate(notebook.get("cells", [])):
            if cell.get("attachments"):
                issues.append(f"Notebook attachment present: {path.relative_to(root)} cell {index}")
            if cell.get("cell_type") == "code":
                if cell.get("outputs"):
                    issues.append(f"Notebook output present: {path.relative_to(root)} cell {index}")
                if cell.get("execution_count") is not None:
                    issues.append(f"Execution count present: {path.relative_to(root)} cell {index}")
        allowed_metadata = {"kernelspec", "language_info"}
        extra = set(notebook.get("metadata", {})) - allowed_metadata
        if extra:
            issues.append(f"Unexpected notebook metadata: {path.relative_to(root)} {sorted(extra)}")
    return issues


def notebook_syntax_issues(root: Path) -> list[str]:
    """Parse every code cell as Python so CI catches structurally invalid notebooks."""

    issues: list[str] = []
    for path in root.rglob("*.ipynb"):
        with path.open(encoding="utf-8") as stream:
            notebook = json.load(stream)
        for index, cell in enumerate(notebook.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            try:
                ast.parse(source)
            except SyntaxError as error:
                issues.append(
                    f"Notebook Python syntax error: {path.relative_to(root)} cell {index}: "
                    f"{error.msg}"
                )
    return issues


def markdown_link_issues(root: Path) -> list[str]:
    """Check relative Markdown links without making network requests."""

    issues: list[str] = []
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in _MARKDOWN_LINK.findall(text):
            clean = target.strip().split(maxsplit=1)[0].strip("<>")
            if not clean or clean.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(clean.split("#", 1)[0])
            if relative and not (path.parent / relative).resolve().exists():
                issues.append(f"Broken relative link in {path.relative_to(root)}: {clean}")
    return issues


def release_safety_issues(root: Path) -> list[str]:
    """Scan public files for unsafe file types, local paths, and unfinished text."""

    issues: list[str] = []
    for path in iter_release_files(root):
        relative = path.relative_to(root)
        lower_name = path.name.lower()
        if lower_name.endswith(_PATIENT_FILE_SUFFIXES):
            issues.append(f"Disallowed patient-data-capable file type: {relative}")
            continue
        if path.stat().st_size > 100 * 1024 * 1024:
            issues.append(f"File exceeds 100 MiB: {relative}")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in _PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                issues.append(f"Private or runtime-local path in {relative}")
                break
        lower_text = text.lower()
        for marker in _UNFINISHED_MARKERS:
            if marker in lower_text:
                issues.append(f"Unfinished marker in {relative}: {marker}")
                break
        for pattern in _CREDENTIAL_PATTERNS:
            if pattern.search(text):
                issues.append(f"Credential-like value in {relative}")
                break
        for pattern in _DEVELOPMENT_TRACE_PATTERNS:
            if pattern.search(text):
                issues.append(f"Development-trace marker in {relative}")
                break
    issues.extend(notebook_output_issues(root))
    issues.extend(notebook_syntax_issues(root))
    issues.extend(markdown_link_issues(root))
    return issues


def validate_release(root: Path) -> list[str]:
    """Run all checks that are safe and deterministic in a public clone."""

    issues = validate_aggregate_directory(root / "results" / "aggregate")
    license_path = root / "LICENSE"
    if not license_path.is_file() or not license_path.read_text(encoding="utf-8").startswith(
        "MIT License"
    ):
        issues.append("Missing or invalid MIT license")
    issues.extend(release_safety_issues(root))
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    issues = validate_release(args.root.resolve())
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    print("Release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
