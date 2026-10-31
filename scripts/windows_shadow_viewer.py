"""Standalone offline read-only SHADOW viewer. Standard-library Tkinter only."""
import json
import tkinter as tk
from tkinter import ttk
from core_ai_tra_son.decision_diagnostic import diagnose_decision

def snapshot(march_available=0):
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

def main():
    root=tk.Tk()
    root.title("Core AI Trà Sơn — SHADOW Viewer v2.5.0")
    root.geometry("600x350")
    frm=ttk.Frame(root,padding=18)
    frm.pack(fill="both",expand=True)
    ttk.Label(frm,text="Core AI Trà Sơn | Offline SHADOW",font=("Segoe UI",16,"bold")).pack(anchor="w")
    ttk.Label(frm,text="Synthetic demo only. No host actions or production integration.").pack(anchor="w",pady=8)
    output=tk.Text(frm,height=12,width=65)
    output.pack(fill="both",expand=True)
    def refresh():
        output.delete("1.0","end")
        output.insert("end",json.dumps(snapshot(),ensure_ascii=False,indent=2))
    ttk.Button(frm,text="Evaluate synthetic demo",command=refresh).pack(anchor="w",pady=10)
    refresh()
    root.mainloop()

if __name__=="__main__":
    main()
