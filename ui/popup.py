"""
Approval Popup — Pinterest-aesthetic desktop UI.
Clean, white, card-based, warm and visual.
"""

import tkinter as tk
from tkinter import scrolledtext
import webbrowser


COLORS = {
    "bg":       "#FFF8F5",
    "surface":  "#FFFFFF",
    "card":     "#FFF0EB",
    "accent":   "#E60023",
    "teal":     "#00736B",
    "amber":    "#CC7722",
    "text":     "#111111",
    "muted":    "#767676",
    "border":   "#E8E8E8",
    "tag_bg":   "#F0FAF9",
    "tag_fg":   "#00736B",
    "progress": "#E60023",
}


def show_approval_popup(jobs: list) -> list:
    if not jobs:
        return []

    state = {"index": 0, "results": []}
    root  = tk.Tk()
    root.title("JobHunter")
    root.configure(bg=COLORS["bg"])
    root.geometry("880x700")
    root.resizable(True, True)

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(root, bg=COLORS["surface"], pady=12)
    topbar.pack(fill="x")

    tk.Label(topbar, text="✦ JobHunter",
             font=("Georgia", 18, "bold"),
             bg=COLORS["surface"], fg=COLORS["accent"]
    ).pack(side="left", padx=24)

    counter_lbl = tk.Label(topbar, text=f"1 of {len(jobs)} matches",
                           font=("Helvetica", 11),
                           bg=COLORS["surface"], fg=COLORS["muted"])
    counter_lbl.pack(side="right", padx=24)

    # ── Progress bar ──────────────────────────────────────────────────────
    prog_bg = tk.Frame(root, bg=COLORS["border"], height=4)
    prog_bg.pack(fill="x")
    prog_fill = tk.Frame(prog_bg, bg=COLORS["progress"], height=4)
    prog_fill.place(relwidth=1/len(jobs), relheight=1)

    # ── Scrollable content area ───────────────────────────────────────────
    content_frame = tk.Frame(root, bg=COLORS["bg"])
    content_frame.pack(fill="both", expand=True, padx=32, pady=20)

    # Score pill + platform
    pill_row = tk.Frame(content_frame, bg=COLORS["bg"])
    pill_row.pack(fill="x", pady=(0, 8))

    score_pill = tk.Label(pill_row, text="",
                          font=("Helvetica", 13, "bold"),
                          bg=COLORS["accent"], fg="white",
                          padx=12, pady=4)
    score_pill.pack(side="left")

    platform_lbl = tk.Label(pill_row, text="",
                            font=("Helvetica", 11),
                            bg=COLORS["bg"], fg=COLORS["muted"])
    platform_lbl.pack(side="left", padx=10)

    # Title
    title_lbl = tk.Label(content_frame, text="",
                         font=("Georgia", 20, "bold"),
                         bg=COLORS["bg"], fg=COLORS["text"],
                         wraplength=780, justify="left")
    title_lbl.pack(anchor="w", pady=(0, 2))

    # Company
    company_lbl = tk.Label(content_frame, text="",
                           font=("Helvetica", 13, "bold"),
                           bg=COLORS["bg"], fg=COLORS["teal"])
    company_lbl.pack(anchor="w")

    # Location
    loc_lbl = tk.Label(content_frame, text="",
                       font=("Helvetica", 11),
                       bg=COLORS["bg"], fg=COLORS["muted"])
    loc_lbl.pack(anchor="w", pady=(2, 10))

    # Match reasons as tags
    tags_frame = tk.Frame(content_frame, bg=COLORS["bg"])
    tags_frame.pack(fill="x", pady=(0, 12))
    tag_labels = []

    # Divider
    tk.Frame(content_frame, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 12))

    # Cover letter label
    tk.Label(content_frame, text="✏️  Cover letter — edit before applying",
             font=("Helvetica", 11, "bold"),
             bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 6))

    cover_box = scrolledtext.ScrolledText(
        content_frame, height=8,
        font=("Helvetica", 12),
        bg=COLORS["surface"], fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="solid", bd=1,
        wrap="word",
        padx=12, pady=10,
    )
    cover_box.pack(fill="both", expand=True)

    # ── Bottom action bar ─────────────────────────────────────────────────
    action_bar = tk.Frame(root, bg=COLORS["surface"], pady=14)
    action_bar.pack(fill="x", side="bottom")

    tk.Frame(action_bar, bg=COLORS["border"], height=1).pack(fill="x", side="top")

    btn_inner = tk.Frame(action_bar, bg=COLORS["surface"])
    btn_inner.pack(padx=24, pady=(10, 0))

    def open_url():
        webbrowser.open(jobs[state["index"]].get("url", ""))

    def record(action):
        job = jobs[state["index"]]
        cl  = cover_box.get("1.0", "end").strip()
        state["results"].append({"job": job, "action": action, "cover_letter": cl})
        advance()

    def advance():
        state["index"] += 1
        if state["index"] >= len(jobs):
            root.destroy()
            return
        load_job(state["index"])
        counter_lbl.config(text=f"{state['index']+1} of {len(jobs)} matches")
        prog_fill.place(relwidth=(state["index"]+1)/len(jobs), relheight=1)

    def load_job(i):
        job   = jobs[i]
        score = job.get("match_score", 0)

        # Score pill color
        if score >= 70:
            pill_color = COLORS["teal"]
        elif score >= 50:
            pill_color = COLORS["amber"]
        else:
            pill_color = COLORS["muted"]

        score_pill.config(text=f"  {score}% match  ", bg=pill_color)
        platform_lbl.config(text=f"via {job.get('platform','').capitalize()}")
        title_lbl.config(text=job.get("title", ""))
        company_lbl.config(text=job.get("company", "") or "")
        loc_lbl.config(text=f"📍  {job.get('location','')}")

        # Rebuild tags
        for w in tags_frame.winfo_children():
            w.destroy()
        for reason in job.get("match_reasons", []):
            tk.Label(tags_frame,
                     text=f"  ✓ {reason}  ",
                     font=("Helvetica", 10),
                     bg=COLORS["tag_bg"], fg=COLORS["tag_fg"],
                     padx=6, pady=3,
                     relief="solid", bd=1
            ).pack(side="left", padx=(0, 6), pady=2)

        cover_box.delete("1.0", "end")
        cover_box.insert("1.0", job.get("cover_letter", ""))

    # Buttons
    tk.Button(btn_inner,
              text="✅  Apply to this job",
              font=("Helvetica", 13, "bold"),
              relief="groove", padx=24, pady=10,
              cursor="hand2",
              command=lambda: record("approve")
    ).pack(side="left", padx=(0, 10))

    tk.Button(btn_inner,
              text="  Skip  ",
              font=("Helvetica", 13),
              bg=COLORS["border"], fg=COLORS["text"],
              relief="flat", padx=20, pady=10,
              cursor="hand2",
              command=lambda: record("skip")
    ).pack(side="left", padx=(0, 10))

    tk.Button(btn_inner,
              text="View listing ↗",
              font=("Helvetica", 11),
              bg=COLORS["surface"], fg=COLORS["teal"],
              relief="flat", padx=14, pady=10,
              cursor="hand2",
              command=open_url
    ).pack(side="left", padx=(0, 20))

    tk.Button(btn_inner,
              text="Skip all remaining",
              font=("Helvetica", 10),
              bg=COLORS["surface"], fg=COLORS["muted"],
              relief="flat", padx=10, pady=10,
              cursor="hand2",
              command=root.destroy
    ).pack(side="left")

    load_job(0)
    root.mainloop()
    return state["results"]
