import json
from pathlib import Path

import pytest

CASES_PATH = Path(__file__).parent / "rag_cases.json"


def load_cases():
    return json.loads(CASES_PATH.read_text())


@pytest.mark.parametrize(
    "case",
    load_cases(),
    ids=lambda case: case["id"],
)
def test_evaluation_case_has_valid_fields(case):
    assert case["question"].strip()
    assert isinstance(case["expected_keywords"], list)
    assert isinstance(case["should_answer"], bool)