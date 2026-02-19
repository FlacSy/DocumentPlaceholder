"""GUI for DocumentPlaceholder — edit configs, preview values, manage database."""

from __future__ import annotations

import sqlite3
import threading
import traceback
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog

import document_placeholder.functions.date  # noqa: F401 — register functions
import document_placeholder.functions.logic  # noqa: F401
import document_placeholder.functions.math  # noqa: F401
import document_placeholder.functions.string  # noqa: F401
import document_placeholder.functions.sql as sql_mod
from document_placeholder.config import Config
from document_placeholder.evaluator import Evaluator
from document_placeholder.exporter import export_document
from document_placeholder.highlighter import SqlHighlighter, YamlHighlighter
from document_placeholder.processor import DocumentProcessor

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DocumentPlaceholder")
        self.geometry("1100x720")
        self.minsize(820, 520)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_files()
        self._build_main()
        self._build_status()
        self._bind_shortcuts()

        self.after(100, self._load_config_file)
        self.after(200, self._refresh_tables)

    # ── keyboard shortcuts ──────────────────────────────────────────────────

    def _bind_shortcuts(self):
        for key in ("<Control-s>", "<Control-S>"):
            self.bind(key, self._on_shortcut_save)
        for key in ("<Control-f>", "<Control-F>"):
            self.bind(key, self._on_shortcut_find)
        self.bind("<F5>", self._on_shortcut_f5)
        self.bind("<Escape>", self._on_shortcut_escape)

    def _on_shortcut_save(self, _event=None):
        self._save_config()
        return "break"

    def _on_shortcut_find(self, _event=None):
        self._toggle_search()
        return "break"

    def _on_shortcut_f5(self, _event=None):
        current = self.tabview.get()
        if current == "Editor":
            self._on_preview()
        elif current == "Database":
            self._refresh_tables()
        return "break"

    def _on_shortcut_escape(self, _event=None):
        if self._search_visible:
            self._hide_search()
            return "break"
        return None

    # ── layout ──────────────────────────────────────────────────────────────

    def _build_header(self):
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=0, column=0, padx=24, pady=(16, 6), sticky="ew")

        ctk.CTkLabel(
            box,
            text="DocumentPlaceholder",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            box,
            text="Edit config, preview values, generate document",
            text_color="gray",
        ).pack(side="left", padx=(12, 0))

    def _build_files(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=20, pady=(0, 6), sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(4, weight=1)

        lbl_w = 80

        ctk.CTkLabel(frame, text="Config:", width=lbl_w, anchor="w").grid(
            row=0, column=0, padx=(14, 2), pady=(10, 4), sticky="w"
        )
        self.config_var = ctk.StringVar(value="template.yaml")
        ctk.CTkEntry(frame, textvariable=self.config_var, height=28).grid(
            row=0, column=1, padx=2, pady=(10, 4), sticky="ew"
        )
        ctk.CTkButton(
            frame, text="...", width=30, height=28, command=self._browse_config
        ).grid(row=0, column=2, padx=(2, 16), pady=(10, 4))

        ctk.CTkLabel(frame, text="Template:", width=lbl_w, anchor="w").grid(
            row=0, column=3, padx=(16, 2), pady=(10, 4), sticky="w"
        )
        self.template_var = ctk.StringVar(value="template.docx")
        ctk.CTkEntry(frame, textvariable=self.template_var, height=28).grid(
            row=0, column=4, padx=2, pady=(10, 4), sticky="ew"
        )
        ctk.CTkButton(
            frame, text="...", width=30, height=28, command=self._browse_template
        ).grid(row=0, column=5, padx=(2, 14), pady=(10, 4))

        ctk.CTkLabel(frame, text="Output:", width=lbl_w, anchor="w").grid(
            row=1, column=0, padx=(14, 2), pady=(4, 10), sticky="w"
        )
        self.output_var = ctk.StringVar(value="output.docx")
        ctk.CTkEntry(frame, textvariable=self.output_var, height=28).grid(
            row=1, column=1, padx=2, pady=(4, 10), sticky="ew"
        )
        ctk.CTkButton(
            frame, text="...", width=30, height=28, command=self._browse_output
        ).grid(row=1, column=2, padx=(2, 16), pady=(4, 10))

        ctk.CTkLabel(frame, text="Database:", width=lbl_w, anchor="w").grid(
            row=1, column=3, padx=(16, 2), pady=(4, 10), sticky="w"
        )
        self.db_var = ctk.StringVar(value="data.db")
        ctk.CTkEntry(frame, textvariable=self.db_var, height=28).grid(
            row=1, column=4, padx=2, pady=(4, 10), sticky="ew"
        )
        ctk.CTkButton(
            frame, text="...", width=30, height=28, command=self._browse_db
        ).grid(row=1, column=5, padx=(2, 14), pady=(4, 10))

    # ── main area (tabview) ─────────────────────────────────────────────────

    def _build_main(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")

        editor_tab = self.tabview.add("Editor")
        db_tab = self.tabview.add("Database")

        self._build_editor_tab(editor_tab)
        self._build_db_tab(db_tab)

    # ── editor tab ──────────────────────────────────────────────────────────

    def _build_editor_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        pane = ctk.CTkFrame(parent, fg_color="transparent")
        pane.grid(row=0, column=0, sticky="nsew")
        pane.grid_columnconfigure(0, weight=3)
        pane.grid_columnconfigure(1, weight=2)
        pane.grid_rowconfigure(1, weight=1)

        mono = ctk.CTkFont(family="monospace", size=13)

        ctk.CTkLabel(
            pane,
            text="Config (YAML)",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=8, pady=(4, 2), sticky="w")
        ctk.CTkLabel(
            pane,
            text="Preview",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=1, padx=8, pady=(4, 2), sticky="w")

        editor_box = ctk.CTkFrame(pane, fg_color="transparent")
        editor_box.grid(row=1, column=0, padx=(8, 4), pady=(0, 8), sticky="nsew")
        editor_box.grid_columnconfigure(0, weight=1)
        editor_box.grid_rowconfigure(1, weight=1)

        self._build_search_bar(editor_box, mono)

        self.editor = ctk.CTkTextbox(editor_box, font=mono, wrap="none", undo=True)
        self.editor.grid(row=1, column=0, sticky="nsew")

        self._yaml_hl = YamlHighlighter(self.editor._textbox)
        self._yaml_hl_timer: str | None = None
        self.editor.bind("<KeyRelease>", self._schedule_yaml_highlight)

        self.preview = ctk.CTkTextbox(pane, font=mono, wrap="word", state="disabled")
        self.preview.grid(row=1, column=1, padx=(4, 8), pady=(0, 8), sticky="nsew")

        # Action buttons
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.grid(row=1, column=0, pady=(4, 0), sticky="ew")

        ctk.CTkButton(
            bar, text="Save Config  Ctrl+S", width=160, command=self._save_config
        ).pack(side="left", padx=(0, 8))
        self.preview_btn = ctk.CTkButton(
            bar, text="Preview  F5", width=140, command=self._on_preview
        )
        self.preview_btn.pack(side="left", padx=8)
        self.generate_btn = ctk.CTkButton(
            bar,
            text="Generate Document",
            width=180,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_generate,
        )
        self.generate_btn.pack(side="right")

    def _build_search_bar(self, parent, mono_font):
        self._search_visible = False
        self._search_matches: list[tuple[str, str]] = []
        self._search_idx: int = -1

        self.search_frame = ctk.CTkFrame(parent, corner_radius=6)
        self.search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.search_frame.grid_remove()

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._do_search())

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            textvariable=self.search_var,
            placeholder_text="Search...",
            height=28,
            font=mono_font,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=6)

        ctk.CTkButton(
            self.search_frame,
            text="\u25b2",
            width=30,
            height=28,
            command=self._search_prev,
        ).pack(side="left", padx=2, pady=6)
        ctk.CTkButton(
            self.search_frame,
            text="\u25bc",
            width=30,
            height=28,
            command=self._search_next,
        ).pack(side="left", padx=2, pady=6)

        self.search_info_var = ctk.StringVar(value="")
        ctk.CTkLabel(
            self.search_frame, textvariable=self.search_info_var, width=70
        ).pack(side="left", padx=4, pady=6)

        ctk.CTkButton(
            self.search_frame,
            text="\u2715",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=self._hide_search,
        ).pack(side="right", padx=(2, 8), pady=6)

        self.search_entry.bind("<Return>", lambda e: self._search_next())
        self.search_entry.bind("<Shift-Return>", lambda e: self._search_prev())
        self.search_entry.bind("<Escape>", lambda e: self._hide_search())

    # ── database tab ────────────────────────────────────────────────────────

    def _build_db_tab(self, parent):
        parent.grid_columnconfigure(0, weight=0, minsize=260)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        mono = ctk.CTkFont(family="monospace", size=13)

        # ── left panel: table browser ───────────────────────────────────────
        left = ctk.CTkFrame(parent)
        left.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)
        left.grid_rowconfigure(3, weight=1)

        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="ew")
        ctk.CTkLabel(hdr, text="Tables", font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left"
        )
        ctk.CTkButton(
            hdr, text="Refresh", width=70, height=26, command=self._refresh_tables
        ).pack(side="right")

        self._table_list_frame = ctk.CTkScrollableFrame(left, width=230)
        self._table_list_frame.grid(row=1, column=0, padx=10, pady=4, sticky="nsew")
        self._table_list_frame.grid_columnconfigure(0, weight=1)
        self._table_buttons: dict[str, ctk.CTkButton] = {}
        self._selected_table: str | None = None

        ctk.CTkLabel(
            left,
            text="Schema",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=2, column=0, padx=10, pady=(8, 2), sticky="w")

        self.schema_box = ctk.CTkTextbox(
            left,
            state="disabled",
            font=ctk.CTkFont(family="monospace", size=12),
        )
        self.schema_box.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # ── right panel: SQL console + results ──────────────────────────────
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=2)
        right.grid_rowconfigure(1, weight=3)

        # SQL editor
        sql_frame = ctk.CTkFrame(right)
        sql_frame.grid(row=0, column=0, pady=(0, 4), sticky="nsew")
        sql_frame.grid_columnconfigure(0, weight=1)
        sql_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            sql_frame,
            text="SQL Query",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.sql_editor = ctk.CTkTextbox(sql_frame, font=mono, wrap="word")
        self.sql_editor.grid(row=1, column=0, padx=12, pady=(0, 4), sticky="nsew")
        self.sql_editor.bind(
            "<Control-Return>", lambda e: (self._execute_sql(), "break")[-1]
        )
        self.sql_editor.bind(
            "<Control-KP_Enter>", lambda e: (self._execute_sql(), "break")[-1]
        )

        self._sql_hl = SqlHighlighter(self.sql_editor._textbox)
        self._sql_hl_timer: str | None = None
        self.sql_editor.bind("<KeyRelease>", self._schedule_sql_highlight)

        btn_bar = ctk.CTkFrame(sql_frame, fg_color="transparent")
        btn_bar.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

        self.sql_exec_btn = ctk.CTkButton(
            btn_bar,
            text="Execute  Ctrl+Enter",
            width=170,
            command=self._execute_sql,
        )
        self.sql_exec_btn.pack(side="left")
        ctk.CTkButton(
            btn_bar,
            text="Clear",
            width=70,
            command=lambda: self.sql_editor.delete("1.0", "end"),
        ).pack(side="left", padx=(8, 0))

        # Results
        res_frame = ctk.CTkFrame(right)
        res_frame.grid(row=1, column=0, pady=(4, 0), sticky="nsew")
        res_frame.grid_columnconfigure(0, weight=1)
        res_frame.grid_rowconfigure(1, weight=1)

        self.result_info_var = ctk.StringVar(value="Results")
        ctk.CTkLabel(
            res_frame,
            textvariable=self.result_info_var,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.result_box = ctk.CTkTextbox(
            res_frame,
            font=mono,
            wrap="none",
            state="disabled",
        )
        self.result_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

    # ── status bar ──────────────────────────────────────────────────────────

    def _build_status(self):
        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            anchor="w",
            text_color="gray",
        ).grid(row=3, column=0, padx=24, pady=(0, 10), sticky="ew")

    # ── search ──────────────────────────────────────────────────────────────

    def _toggle_search(self):
        if self._search_visible:
            self._hide_search()
        else:
            self._show_search()

    def _show_search(self):
        self._search_visible = True
        self.search_frame.grid()
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")

    def _hide_search(self):
        self._search_visible = False
        self.search_frame.grid_remove()
        self._clear_search_tags()
        self.search_info_var.set("")
        self.editor.focus_set()

    def _do_search(self):
        if not hasattr(self, "editor"):
            return
        self._clear_search_tags()

        term = self.search_var.get()
        if not term:
            self.search_info_var.set("")
            self._search_matches = []
            self._search_idx = -1
            return

        tb = self.editor._textbox
        tb.tag_config("search_hl", background="#3D5A80", foreground="#FFFFFF")
        tb.tag_config("search_cur", background="#EE6C00", foreground="#FFFFFF")

        self._search_matches = []
        pos = "1.0"
        while True:
            pos = tb.search(term, pos, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(term)}c"
            self._search_matches.append((pos, end))
            tb.tag_add("search_hl", pos, end)
            pos = end

        if self._search_matches:
            self._search_idx = 0
            self._highlight_current_match()
        else:
            self._search_idx = -1
            self.search_info_var.set("No results")

    def _highlight_current_match(self):
        tb = self.editor._textbox
        tb.tag_remove("search_cur", "1.0", "end")
        if 0 <= self._search_idx < len(self._search_matches):
            p, e = self._search_matches[self._search_idx]
            tb.tag_add("search_cur", p, e)
            tb.tag_raise("search_cur")
            tb.see(p)
            self.search_info_var.set(
                f"{self._search_idx + 1}/{len(self._search_matches)}"
            )

    def _search_next(self):
        if self._search_matches:
            self._search_idx = (self._search_idx + 1) % len(self._search_matches)
            self._highlight_current_match()

    def _search_prev(self):
        if self._search_matches:
            self._search_idx = (self._search_idx - 1) % len(self._search_matches)
            self._highlight_current_match()

    def _clear_search_tags(self):
        if hasattr(self, "editor"):
            tb = self.editor._textbox
            tb.tag_remove("search_hl", "1.0", "end")
            tb.tag_remove("search_cur", "1.0", "end")

    # ── syntax highlighting (debounced) ─────────────────────────────────────

    def _schedule_yaml_highlight(self, _event=None):
        if self._yaml_hl_timer:
            self.after_cancel(self._yaml_hl_timer)
        self._yaml_hl_timer = self.after(100, self._apply_yaml_highlight)

    def _apply_yaml_highlight(self):
        self._yaml_hl.apply()
        tb = self.editor._textbox
        for t in ("search_hl", "search_cur"):
            if t in tb.tag_names():
                tb.tag_raise(t)

    def _schedule_sql_highlight(self, _event=None):
        if self._sql_hl_timer:
            self.after_cancel(self._sql_hl_timer)
        self._sql_hl_timer = self.after(100, self._sql_hl.apply)

    # ── browse dialogs ──────────────────────────────────────────────────────

    def _browse_config(self):
        p = filedialog.askopenfilename(
            title="Select config", filetypes=[("YAML", "*.yaml *.yml"), ("All", "*.*")]
        )
        if p:
            self.config_var.set(p)
            self._load_config_file(p)

    def _browse_template(self):
        p = filedialog.askopenfilename(
            title="Select template", filetypes=[("Word", "*.docx"), ("All", "*.*")]
        )
        if p:
            self.template_var.set(p)

    def _browse_output(self):
        p = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".docx",
            filetypes=[("Word", "*.docx"), ("PDF", "*.pdf"), ("All", "*.*")],
        )
        if p:
            self.output_var.set(p)

    def _browse_db(self):
        p = filedialog.askopenfilename(
            title="Select database",
            filetypes=[("SQLite", "*.db *.sqlite"), ("All", "*.*")],
        )
        if p:
            self.db_var.set(p)
            self._refresh_tables()

    # ── file helpers ────────────────────────────────────────────────────────

    def _load_config_file(self, path: str | None = None):
        path = path or self.config_var.get()
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.after(10, self._apply_yaml_highlight)
            self.status_var.set(f"Loaded: {path}")
        except FileNotFoundError:
            self.status_var.set(f"File not found: {path}")
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def _save_config(self):
        path = self.config_var.get()
        content = self.editor.get("1.0", "end-1c")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            self.status_var.set(f"Saved: {path}")
        except Exception as exc:
            self.status_var.set(f"Error saving: {exc}")

    # ── editor: preview ─────────────────────────────────────────────────────

    def _set_preview(self, text: str):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def _on_preview(self):
        yaml_text = self.editor.get("1.0", "end-1c")
        db_path = self.db_var.get()
        self.preview_btn.configure(state="disabled", text="Loading...")
        threading.Thread(
            target=self._do_preview,
            args=(yaml_text, db_path),
            daemon=True,
        ).start()

    def _do_preview(self, yaml_text: str, db_path: str):
        try:
            config = Config.from_string(yaml_text)
            sql_mod.init(db_path)
            evaluator = Evaluator()

            for expr in config.on_start:
                evaluator.evaluate_value(expr)

            keys = list(config.placeholders.keys())
            pad = max((len(k) for k in keys), default=0)
            values: dict[str, object] = {}
            lines: list[str] = []
            for key in keys:
                try:
                    val = evaluator.evaluate_value(config.placeholders[key])
                    values[key] = val
                    lines.append(f"{key:<{pad}}  =  {val}")
                except Exception as exc:
                    lines.append(f"{key:<{pad}}  =  ERROR: {exc}")

            # Show output name & formats
            output_path = Path(self.output_var.get())
            if config.output_name:
                base = evaluator.resolve_output_name(config.output_name, values)
            else:
                base = output_path.stem
            fmts = config.output_format
            if not fmts:
                ext = output_path.suffix.lstrip(".").lower()
                fmts = [ext if ext else "docx"]

            lines.append("")
            lines.append(f"Output: {base} [{', '.join(fmts)}]")

            self.after(0, self._set_preview, "\n".join(lines))
            self.after(0, lambda: self.status_var.set("Preview refreshed"))
        except Exception as exc:
            self.after(0, self._set_preview, f"Error:\n{exc}")
            self.after(0, lambda: self.status_var.set("Preview error"))
        finally:
            sql_mod.close()
            self.after(
                0,
                lambda: self.preview_btn.configure(state="normal", text="Preview  F5"),
            )

    # ── editor: generate ────────────────────────────────────────────────────

    def _on_generate(self):
        yaml_text = self.editor.get("1.0", "end-1c")
        tpl = self.template_var.get()
        out = self.output_var.get()
        db = self.db_var.get()
        self.generate_btn.configure(state="disabled", text="Generating...")
        threading.Thread(
            target=self._do_generate,
            args=(yaml_text, tpl, out, db),
            daemon=True,
        ).start()

    def _do_generate(self, yaml_text: str, tpl: str, out: str, db: str):
        try:
            config = Config.from_string(yaml_text)
            sql_mod.init(db)
            evaluator = Evaluator()

            for expr in config.on_start:
                evaluator.evaluate_value(expr)

            values: dict[str, object] = {}
            keys = list(config.placeholders.keys())
            pad = max((len(k) for k in keys), default=0)
            lines: list[str] = []
            for key in keys:
                values[key] = evaluator.evaluate_value(config.placeholders[key])
                lines.append(f"{key:<{pad}}  =  {values[key]}")

            # Resolve output name and formats
            output_arg = Path(out)
            output_dir = output_arg.parent or Path(".")
            if config.output_name:
                base_name = evaluator.resolve_output_name(config.output_name, values)
            else:
                base_name = output_arg.stem
            fmts = config.output_format
            if not fmts:
                ext = output_arg.suffix.lstrip(".").lower()
                fmts = [ext if ext else "docx"]

            lines.append("")
            lines.append(f"Output: {base_name} [{', '.join(fmts)}]")
            self.after(0, self._set_preview, "\n".join(lines))

            # Fill template
            processor = DocumentProcessor(tpl)
            processor.replace_placeholders(values)

            # Save docx (always needed as conversion source)
            docx_path = output_dir / f"{base_name}.docx"
            processor.save(str(docx_path))

            generated: list[Path] = []
            for fmt in fmts:
                if fmt == "docx":
                    generated.append(docx_path)
                else:
                    target = output_dir / f"{base_name}.{fmt}"
                    export_document(str(docx_path), str(target))
                    generated.append(target)

            if "docx" not in fmts:
                docx_path.unlink(missing_ok=True)

            for expr in config.on_end:
                evaluator.evaluate_value(expr)

            result_str = ", ".join(str(g) for g in generated)
            self.after(0, lambda: self.status_var.set(f"Done -> {result_str}"))
        except Exception as exc:
            msg = f"Error:\n{exc}\n\n{traceback.format_exc()}"
            self.after(0, self._set_preview, msg)
            self.after(0, lambda: self.status_var.set("Generation failed"))
        finally:
            sql_mod.close()
            self.after(
                0,
                lambda: self.generate_btn.configure(
                    state="normal", text="Generate Document"
                ),
            )

    # ── database: table browser ─────────────────────────────────────────────

    def _refresh_tables(self):
        db_path = self.db_var.get()

        for w in self._table_list_frame.winfo_children():
            w.destroy()
        self._table_buttons.clear()
        self._selected_table = None
        self._set_schema("")

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            tables = [r[0] for r in cur.fetchall()]

            for tbl in tables:
                cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
                cnt = cur.fetchone()[0]
                btn = ctk.CTkButton(
                    self._table_list_frame,
                    text=f"{tbl}  ({cnt})",
                    anchor="w",
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray75", "gray30"),
                    height=30,
                    command=lambda t=tbl: self._on_table_click(t),
                )
                btn.grid(sticky="ew", pady=1)
                self._table_buttons[tbl] = btn

            conn.close()
            self.status_var.set(f"Database: {len(tables)} table(s) in {db_path}")
        except Exception as exc:
            self.status_var.set(f"DB error: {exc}")

    def _on_table_click(self, table_name: str):
        if self._selected_table and self._selected_table in self._table_buttons:
            self._table_buttons[self._selected_table].configure(fg_color="transparent")

        self._selected_table = table_name
        self._table_buttons[table_name].configure(fg_color=("gray75", "gray35"))

        self._show_table_schema(table_name)

        self.sql_editor.delete("1.0", "end")
        self.sql_editor.insert("1.0", f'SELECT * FROM "{table_name}" LIMIT 100;')
        self._schedule_sql_highlight()

    def _show_table_schema(self, table_name: str):
        db_path = self.db_var.get()
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            cur.execute(f'PRAGMA table_info("{table_name}")')
            columns = cur.fetchall()

            cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cur.fetchone()[0]
            conn.close()

            lines = [f"Table: {table_name}", f"Rows:  {count}", ""]
            name_w = max((len(c[1]) for c in columns), default=4)
            for col in columns:
                _, name, type_, notnull, default, pk = col
                parts = [f"  {name:<{name_w}}  {type_}"]
                if pk:
                    parts.append(" PK")
                if notnull:
                    parts.append(" NOT NULL")
                if default is not None:
                    parts.append(f" DEFAULT {default}")
                lines.append("".join(parts))

            self._set_schema("\n".join(lines))
        except Exception as exc:
            self._set_schema(f"Error: {exc}")

    def _set_schema(self, text: str):
        self.schema_box.configure(state="normal")
        self.schema_box.delete("1.0", "end")
        self.schema_box.insert("1.0", text)
        self.schema_box.configure(state="disabled")

    # ── database: SQL execution ─────────────────────────────────────────────

    def _execute_sql(self):
        query = self.sql_editor.get("1.0", "end-1c").strip()
        if not query:
            return

        db_path = self.db_var.get()
        self.sql_exec_btn.configure(state="disabled")

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(query)

            if cur.description:
                rows = cur.fetchall()
                text = self._format_query_results(cur.description, rows)
                self._set_result(text)
                self.result_info_var.set(f"Results  ({len(rows)} rows)")
            else:
                conn.commit()
                affected = cur.rowcount
                self._set_result(f"Query OK. Rows affected: {affected}")
                self.result_info_var.set("Results")
                self._refresh_tables()

            conn.close()
            self.status_var.set("Query executed")
        except Exception as exc:
            self._set_result(f"Error:\n{exc}")
            self.status_var.set("Query error")
        finally:
            self.sql_exec_btn.configure(state="normal")

    @staticmethod
    def _format_query_results(description, rows: list) -> str:
        columns = [d[0] for d in description]

        col_w = [len(c) for c in columns]
        for row in rows:
            for i, val in enumerate(row):
                col_w[i] = max(col_w[i], len(str(val) if val is not None else "NULL"))

        hdr = " | ".join(c.ljust(col_w[i]) for i, c in enumerate(columns))
        sep = "-+-".join("-" * w for w in col_w)

        lines = [hdr, sep]
        for row in rows:
            cells = [str(v) if v is not None else "NULL" for v in row]
            lines.append(
                " | ".join(cells[i].ljust(col_w[i]) for i in range(len(cells)))
            )

        n = len(rows)
        lines.append(f"\n({n} row{'s' if n != 1 else ''})")
        return "\n".join(lines)

    def _set_result(self, text: str):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")


def main() -> None:
    """Entry point for the ``docplaceholder-gui`` console command."""
    App().mainloop()


if __name__ == "__main__":
    main()
