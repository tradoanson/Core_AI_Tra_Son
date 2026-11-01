"""Standalone offline read-only SHADOW viewer. Standard-library Tkinter only."""
import argparse
import json
import tkinter as tk
from tkinter import ttk
from core_ai_tra_son.shadow_snapshot import shadow_snapshot

def snapshot(march_available=0):
    """Backward-compatible viewer entry point; engine stays GUI-independent."""
    return shadow_snapshot(march_available)

def main():
    root=tk.Tk()
    root.title("Core AI Trà Sơn — SHADOW Viewer v3.1.0")
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
    parser=argparse.ArgumentParser(description="Offline SHADOW viewer")
    parser.add_argument("--self-test",action="store_true",help="Headless synthetic diagnostic for packaged EXE")
    args=parser.parse_args()
    if args.self_test:
        result=snapshot()
        print(json.dumps(result,ensure_ascii=True,sort_keys=True))
        raise SystemExit(0 if result["mode"]=="OFFLINE_SHADOW" and not result["action_executed"] else 1)
    main()
