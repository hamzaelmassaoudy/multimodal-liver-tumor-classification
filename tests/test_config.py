from pathlib import Path

import yaml

from liver_tumor_pipeline.config import load_config, require_path
from liver_tumor_pipeline.radiomics import validate_radiomics_config

ROOT = Path(__file__).resolve().parents[1]


def test_environment_path_expansion(monkeypatch, tmp_path):
    data_root = tmp_path / "dataset"
    data_root.mkdir()
    config_path = tmp_path / "paths.yaml"
    config_path.write_text("paths:\n  data: ${PUBLIC_TEST_DATA_ROOT}\n", encoding="utf-8")
    monkeypatch.setenv("PUBLIC_TEST_DATA_ROOT", str(data_root))
    config = load_config(config_path)
    assert require_path(config, "data") == data_root


def test_public_path_template_contains_only_environment_variables():
    config = load_config(ROOT / "configs" / "paths.example.yaml", expand_environment=False)
    values = config["paths"].values()
    assert all(value.startswith("${") and value.endswith("}") for value in values)


def test_radiomics_configuration_matches_historical_specification():
    with (ROOT / "configs" / "radiomics.yaml").open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_radiomics_config(config)


def test_training_configuration_locks_crop_and_fusion():
    with (ROOT / "configs" / "training.yaml").open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    assert config["crop_size"] == 96
    assert config["cross_validation_folds"] == 5
    assert config["fusion"]["include_w3"] is False


def test_citation_metadata_is_complete_and_does_not_invent_identifiers():
    with (ROOT / "CITATION.cff").open(encoding="utf-8") as stream:
        citation = yaml.safe_load(stream)
    assert citation["cff-version"] == "1.2.0"
    assert citation["version"] == "1.1.0"
    names = [(author["given-names"], author["family-names"]) for author in citation["authors"]]
    assert names == [("Xuezhi", "Wen"), ("Hamza", "El Massaoudy")]
    assert citation["license"] == "MIT"
    assert "doi" not in citation


def test_mit_license_is_complete():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License")
    assert "Wen Xuezhi and Hamza El Massaoudy" in license_text
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in license_text
