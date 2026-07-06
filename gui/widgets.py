# @build: 2026-07-06.08-00-00 | id: GUI-105 | desc: Widgets con bombillito azul para seleccionada, IterationMarker, glass simulado
import customtkinter as ctk
import re

# ------------------------------------------------------------
# NodeButton (agente con semáforo)
# ------------------------------------------------------------
class NodeButton(ctk.CTkFrame):
    def __init__(self, master, node_data, on_click, status="inactive"):
        super().__init__(master, corner_radius=10, fg_color="#1e1e1e", width=110, height=115)
        self.node_data = node_data
        self.pack_propagate(False)
        nid, name, provider, model, role, emoji, score, s_cnt, f_cnt, lat, base_url = node_data

        self.emoji_label = ctk.CTkLabel(self, text=emoji, font=("Segoe UI Emoji", 26))
        self.emoji_label.pack(pady=(5, 0))
        self.name_label = ctk.CTkLabel(self, text=name[:12], font=("Segoe UI", 10, "bold"), text_color="#cccccc")
        self.name_label.pack()
        score_color = "#2ecc71" if score > 1000 else "#e74c3c" if score < 800 else "#f1c40f"
        ctk.CTkLabel(self, text=f"Score: {score:.0f}", font=("Segoe UI", 9), text_color=score_color).pack()

        self.status_indicator = ctk.CTkLabel(self, text="", width=8, height=8, corner_radius=4)
        self.status_indicator.place(relx=1.0, rely=0.0, anchor="ne")
        self.update_status(status)

        self.bind("<Button-1>", lambda e: on_click(self.node_data))
        self.emoji_label.bind("<Button-1>", lambda e: on_click(self.node_data))
        self.name_label.bind("<Button-1>", lambda e: on_click(self.node_data))

    def update_status(self, status):
        colors = {
            "active": "#2ecc71",
            "thinking": "#3498db",
            "warning": "#f1c40f",
            "error": "#e74c3c",
            "inactive": "#7f8c8d",
            "selected": "#3498db"
        }
        bgs = {
            "active": "#1a3a1a",
            "thinking": "#1a2a4a",
            "warning": "#3a3a00",
            "error": "#3a0000",
            "inactive": "#1e1e1e",
            "selected": "#1a2a4a"  # same as thinking, but will not be used for background in selected (background stays as original)
        }
        self.status_indicator.configure(fg_color=colors.get(status, "#7f8c8d"))
        # For 'selected', we do NOT change the background; keep it as the original state
        if status != "selected":
            self.configure(fg_color=bgs.get(status, "#1e1e1e"))

# ------------------------------------------------------------
# UserBubble (burbuja de vidrio del usuario, opacidad simulada)
# ------------------------------------------------------------
class UserBubble(ctk.CTkFrame):
    def __init__(self, master, content, on_copy=None, on_save=None):
        super().__init__(master, corner_radius=16, fg_color="#1e1e1e", border_width=1, border_color="#333333")
        chat_width = master.winfo_width() if master.winfo_width() > 200 else 800
        max_width = int(chat_width * 0.6)
        self.configure(width=max_width)
        self.pack(fill="x", pady=12, padx=(max_width, 20), anchor="e")

        ctk.CTkLabel(self, text="👤 Tú", font=("Segoe UI", 10), text_color="#cccccc").pack(anchor="w", padx=10, pady=(8, 0))

        lines = content.count('\n') + 1
        height = min(300, max(40, lines * 22 + 20))
        txt = ctk.CTkTextbox(self, font=("Segoe UI", 13), height=height, wrap="word",
                             fg_color="transparent", text_color="#e0e0e0", border_width=0)
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=10, pady=(2, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(anchor="e", padx=5, pady=(0, 5))
        if on_copy:
            ctk.CTkButton(btn_frame, text="📋", width=24, height=24,
                          fg_color="transparent", text_color="#888888", hover_color="#444444",
                          font=("Segoe UI", 11), command=lambda: on_copy(content)).pack(side="left", padx=2)
        if on_save:
            ctk.CTkButton(btn_frame, text="💾", width=24, height=24,
                          fg_color="transparent", text_color="#888888", hover_color="#444444",
                          font=("Segoe UI", 11), command=lambda: on_save(content)).pack(side="left", padx=2)

# ------------------------------------------------------------
# ThinkingBlock (bloque de razonamiento colapsable)
# ------------------------------------------------------------
class ThinkingBlock(ctk.CTkFrame):
    def __init__(self, master, content, collapsed=False):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.pack(fill="x", pady=5, padx=20, anchor="w")
        self.collapsed = collapsed

        self.line = ctk.CTkFrame(self, width=3, fg_color="#444444")
        self.line.pack(side="left", fill="y", padx=(0, 8))

        self.toggle_btn = ctk.CTkButton(self, text="▶" if collapsed else "▼", width=20,
                                        fg_color="transparent", text_color="#888888",
                                        command=self._toggle)
        self.toggle_btn.pack(side="left", anchor="n")

        ctk.CTkLabel(self, text="Razonamiento", font=("Segoe UI", 10, "italic"), text_color="#888888").pack(side="left", padx=5)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        if not collapsed:
            self.content_frame.pack(fill="x", padx=10, pady=(5, 0))
        txt = ctk.CTkTextbox(self.content_frame, font=("Segoe UI", 12, "italic"), height=min(200, content.count('\n')*20+40),
                             wrap="word", fg_color="transparent", text_color="#aaaaaa", border_width=0)
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="x")

    def _toggle(self):
        if self.collapsed:
            self.content_frame.pack(fill="x", padx=10, pady=(5, 0))
            self.toggle_btn.configure(text="▼")
        else:
            self.content_frame.pack_forget()
            self.toggle_btn.configure(text="▶")
        self.collapsed = not self.collapsed

    def set_content(self, new_text):
        # Update text if needed (for state updates)
        for w in self.content_frame.winfo_children():
            w.destroy()
        txt = ctk.CTkTextbox(self.content_frame, font=("Segoe UI", 12, "italic"), height=min(200, new_text.count('\n')*20+40),
                             wrap="word", fg_color="transparent", text_color="#aaaaaa", border_width=0)
        txt.insert("1.0", new_text)
        txt.configure(state="disabled")
        txt.pack(fill="x")

# ------------------------------------------------------------
# IAResponse (respuesta final de la IA sobre fondo negro)
# ------------------------------------------------------------
class IAResponse(ctk.CTkFrame):
    def __init__(self, master, content, ia_name=None, log_id=None,
                 on_execute=None, on_copy=None, on_save=None, on_rate=None):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.content = content
        self.log_id = log_id
        self.pack(fill="x", pady=12, padx=20, anchor="w")

        header_text = f"🤖 {ia_name}" if ia_name else "🤖 IA"
        ctk.CTkLabel(self, text=header_text, font=("Segoe UI", 10), text_color="#888888").pack(anchor="w", padx=5, pady=(5, 0))

        lines = content.count('\n') + 1
        height = min(300, max(40, lines * 22 + 20))
        txt = ctk.CTkTextbox(self, font=("Segoe UI", 13), height=height, wrap="word",
                             fg_color="transparent", text_color="#e0e0e0", border_width=0)
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=5, pady=(2, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=5, pady=(0, 5))

        if on_rate:
            ctk.CTkButton(btn_frame, text="👍", width=24, height=24,
                          fg_color="transparent", text_color="#666666", hover_color="#333333",
                          font=("Segoe UI", 11), command=lambda: on_rate(5, self)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="👎", width=24, height=24,
                          fg_color="transparent", text_color="#666666", hover_color="#333333",
                          font=("Segoe UI", 11), command=lambda: on_rate(1, self)).pack(side="left", padx=2)

        if on_execute:
            for m in re.finditer(r"```(\w+)\n(.*?)```", content, re.DOTALL):
                lang, code = m.group(1), m.group(2).strip()
                ctk.CTkButton(btn_frame, text=f"▶ {lang}", width=50, height=24,
                              fg_color="transparent", text_color="#666666", hover_color="#333333",
                              font=("Segoe UI", 9), command=lambda c=code, l=lang: on_execute(c, l)).pack(side="left", padx=2)

        if on_copy:
            ctk.CTkButton(btn_frame, text="📋", width=24, height=24,
                          fg_color="transparent", text_color="#666666", hover_color="#333333",
                          font=("Segoe UI", 11), command=lambda: on_copy(content)).pack(side="left", padx=2)

        if on_save:
            ctk.CTkButton(btn_frame, text="💾", width=24, height=24,
                          fg_color="transparent", text_color="#666666", hover_color="#333333",
                          font=("Segoe UI", 11), command=lambda: on_save(content)).pack(side="left", padx=2)

# ------------------------------------------------------------
# MessageBubble (mensajes del sistema, simple)
# ------------------------------------------------------------
class MessageBubble(ctk.CTkFrame):
    def __init__(self, master, role, content, ia_name=None, log_id=None,
                 on_execute=None, on_copy=None, on_save=None, on_rate=None):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.pack(fill="x", pady=5, padx=20, anchor="w")
        ctk.CTkLabel(self, text="⚡ Sistema", font=("Segoe UI", 10), text_color="#888888").pack(anchor="w", padx=5, pady=(5,0))
        txt = ctk.CTkTextbox(self, font=("Segoe UI", 12), height=min(100, content.count('\n')*20+40),
                             wrap="word", fg_color="transparent", text_color="#aaaaaa", border_width=0)
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=5)

# ------------------------------------------------------------
# IterationMarker (línea divisoria sutil)
# ------------------------------------------------------------
class IterationMarker(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=1, fg_color="#333333")
        self.pack(fill="x", padx=40, pady=0)
