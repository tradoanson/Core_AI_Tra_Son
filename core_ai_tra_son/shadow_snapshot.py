"""Pure, GUI-independent offline SHADOW presentation boundary.

No Tkinter, filesystem writes, sockets, host actions or live integrations.
"""
from .decision_diagnostic import diagnose_decision

def shadow_snapshot(march_available=0):
    if type(march_available) is not int or not 0 <= march_available <= 5:
        raise ValueError("synthetic march count 0..5 required")
    diagnostic=diagnose_decision({"march_available":march_available},verified=True)
    return {
        "mode":"OFFLINE_SHADOW",
        "input_kind":"SYNTHETIC_ONLY",
        "selected":diagnostic.selected,
        "status":diagnostic.status,
        "score_margin":diagnostic.margin,
        "confidence_kind":diagnostic.confidence_kind,
        "action_executed":False,
        "production_integrated":False,
    }
