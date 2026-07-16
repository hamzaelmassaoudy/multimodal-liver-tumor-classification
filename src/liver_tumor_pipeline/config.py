"""Configuration loading with explicit environment-variable expansion."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

_ENV_PATTERN = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")


def _expand_environment(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _expand_environment(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_environment(item) for item in value]
    if not isinstance(value, str):
        return value

    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if resolved is None:
            missing.add(name)
            return match.group(0)
        return resolved

    expanded = _ENV_PATTERN.sub(replace, value)
    if missing:
        names = ", ".join(sorted(missing))
        raise KeyError(f"Required environment variables are not set: {names}")
    return expanded


def load_config(path: str | Path, *, expand_environment: bool = True) -> dict[str, Any]:
    """Load a YAML mapping and optionally resolve ``${VARIABLE}`` values."""

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration must contain a mapping: {config_path}")
    return _expand_environment(data) if expand_environment else data


def require_path(config: dict[str, Any], key: str, *, must_exist: bool = True) -> Path:
    """Return one configured path with a clear error for missing private inputs."""

    paths = config.get("paths")
    if not isinstance(paths, dict) or key not in paths:
        raise KeyError(f"Missing configuration key: paths.{key}")
    path = Path(paths[key]).expanduser()
    if must_exist and not path.exists():
        raise FileNotFoundError(
            f"Configured path for paths.{key} is unavailable. "
            "Obtain the required data or private artifact and update configs/paths.yaml."
        )
    return path
