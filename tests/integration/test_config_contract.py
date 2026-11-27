"""Validacao dos contratos de dados CT-001/CT-002/CT-003 (EP-02, Tarefa 2.1)."""

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "configs" / "schemas"


def _schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _default_scenario() -> dict[str, Any]:
    text = (ROOT / "configs" / "default_scenario.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


CT001 = Draft202012Validator(_schema("ct-001-scenario.schema.json"))


@pytest.mark.parametrize(
    "name",
    [
        "ct-001-scenario.schema.json",
        "ct-002-metadata.schema.json",
        "ct-003-metrics.schema.json",
    ],
)
def test_schemas_are_valid_draft_2020_12(name: str) -> None:
    Draft202012Validator.check_schema(_schema(name))


def test_default_scenario_conforms_to_ct001() -> None:
    CT001.validate(_default_scenario())


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("lora_settings", "sf_strategy", "SF_MAGIC"),
        ("topology", "n_devices", 0),
        ("topology", "radius_m", 50),
        ("stochastic", "rng_run", 0),
        ("traffic", "payload_bytes", 300),
    ],
)
def test_invalid_scenarios_are_rejected(section: str, field: str, value: Any) -> None:
    scenario = _default_scenario()
    scenario[section][field] = value
    assert not CT001.is_valid(scenario)


def test_ca001_warmup_shorter_than_duration() -> None:
    scenario = _default_scenario()
    assert scenario["warmup_seconds"] < scenario["duration_seconds"]


def test_ct003_sample_header_matches_schema() -> None:
    expected = [
        c["name"]
        for c in _schema("ct-003-metrics.schema.json")["properties"]["packets_csv"][
            "const"
        ]
    ]
    header = (
        (ROOT / "tests" / "fixtures" / "ct003_packets_sample.csv")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    assert header.split(",") == expected
