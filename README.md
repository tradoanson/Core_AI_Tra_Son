# Core AI Trà Sơn — prototype v0.1.0

Lightweight Python module with three conceptual parts:

- **Micro Agent**: `CoreAI.evaluate()` makes read-only recommendations.
- **Adaptive**: `EtaAdaptive` updates an in-memory ETA bias from verified observations only.
- **Tiny AI placeholder**: `TinyPredictor` implements a deterministic baseline, **not yet a trained machine-learning model**.

## Requirements
Python 3.11+; no third-party dependencies.

## Quick start
From the extracted folder:

```powershell
py -m unittest discover -s tests -v
py -c "from core_ai_tra_son import CoreAI; print(CoreAI('vtnd').evaluate({'march_available': 0, 'verified': True}).to_dict())"
```

## Integration contract
Use `CoreAI('vtnd')` or `CoreAI('nhankhau')`, then call `evaluate(observation)` with a Python dictionary. The return is a suggestion only. No DB connection, file writes, HTTP server, process injection, or execution bridge exists.

### VTND example
```python
CoreAI('vtnd').evaluate({'march_available': 0, 'verified': True})
```

`march_available` is the **number of free marches**, not total marches. `verified` must be True for actionable suggestions. This does not alter Managed V3, scheduler or game workflow.

### Web Nhân Hộ Khẩu example
```python
CoreAI('nhankhau').evaluate({
    'record': {'name': 'Nguyen Van A'},
    'required_fields': ['name', 'birth_date']
})
```

The required fields must be supplied by the host application's authoritative rules. This is only a missing-field checker; it does **not** validate CT01/CT13, residency categories, or legal rules.

## Security boundaries
- Do not send real citizen data to an external model or service.
- Never allow AI suggestions to directly mutate live data.
- Isolate project data and audit logs per deployment.
- No production integration before schema, access control, testing, and approval.

## Roadmap
1. JSON schema and adapter contracts.
2. Per-project audit and policy gateway.
3. Local, measured Tiny ML model with evaluation dataset and rollback.
4. Shadow-mode benchmark against current VTND Adaptive and Web rules.
5. Controlled integration only after explicit authorization.
