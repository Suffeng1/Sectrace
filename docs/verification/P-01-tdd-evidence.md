# P-01 TDD evidence

## Red: contract tests before `contracts.py`

Command:

```text
pytest tests/contracts/test_contracts.py -v
```

Result (before `src/app/contracts.py` existed):

```text
collected 0 items / 1 error
tests/contracts/test_contracts.py:4: in <module>
    from src.app.contracts import IncidentCase, ResponsePlan
E   ModuleNotFoundError: No module named 'src'
```

The test was created before the contract module. The additional `src/__init__.py` and `tests/__init__.py` package markers make the repository import boundary explicit; they do not implement domain behavior.

## Green: Contract v1.0 implementation

Command:

```text
pytest tests/contracts/test_contracts.py -v
```

Result:

```text
collected 2 items
tests/contracts/test_contracts.py::test_valid_incident_case_parses PASSED [ 50%]
tests/contracts/test_contracts.py::test_high_risk_response_requires_approval PASSED [100%]
============================== 2 passed in 0.29s ==============================
```
