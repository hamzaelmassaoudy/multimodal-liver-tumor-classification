from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "synthetic_fusion.py"


def load_example():
    spec = importlib.util.spec_from_file_location("synthetic_fusion_example", EXAMPLE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_evaluation_missing_values_use_training_fold_medians():
    result = load_example().run_example()
    # Including the evaluation age (83) in fitting would change the age median to 57.5.
    np.testing.assert_allclose(result.imputer.statistics_, [55, 1])
    np.testing.assert_allclose(result.evaluation_features[:, 6:], [[55, 1], [83, 0]])
    assert np.isfinite(result.training_features).all()
    assert np.isfinite(result.evaluation_features).all()
    assert result.training_features.shape == (6, 8)
    assert result.evaluation_features.shape == (2, 8)


def test_documented_example_runs_as_a_script():
    process = subprocess.run(
        [sys.executable, str(EXAMPLE)], cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert "Synthetic example only" in process.stdout
    assert "Training-fold clinical medians (age, sex): [55.0, 1.0]" in process.stdout
    assert "Evaluation feature matrix: (2, 8)" in process.stdout
