# @build: 2026-07-06.01-00-00 | id: GUI-103 | desc: Toolbox con refresco seguro (reutiliza contenedores)
import customtkinter as ctk

class Toolbox(ctk.CTkTabview):
    def __init__(self, master, db, on_upload=None, **kwargs):
        super().__init__(master, width=280, **kwargs)
        self.db = db
        self.add("Docs")
        self.add("Prompts")
        self.add("Git")
        self.add("Dash")
        self._setup_docs(on_upload)
        self._setup_prompts()
        self._setup_git()
        self._setup_dash()

    def _setup_docs(self, on_upload):
        tab = self.tab("Docs")
        ctk.CTkButton(tab, text="📂 Subir", command=on_upload).pack(pady=5, side="bottom")
        self._docs_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self._docs_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_prompts(self):
        tab = self.tab("Prompts")
        self._prompts_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self._prompts_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_git(self):
        tab = self.tab("Git")
        token = self.db.get_config("github_token", decrypt=True)
        estado = "Conectado" if token else "Desconectado"
        ctk.CTkLabel(tab, text=f"Estado: {estado}").pack(pady=20)

    def _setup_dash(self):
        tab = self.tab("Dash")
        self._dash_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self._dash_frame.pack(fill="both", expand=True)

    def refresh_docs(self, docs, on_delete):
        for w in self._docs_frame.winfo_children():
            w.destroy()
        if not docs:
            ctk.CTkLabel(self._docs_frame, text="Sin documentos", text_color="gray").pack(pady=20)
            return
        for d in docs:
            f = ctk.CTkFrame(self._docs_frame, fg_color="gray20")
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=d[1], anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            ctk.CTkButton(f, text="🗑", width=25, command=lambda did=d[0]: on_delete(did)).pack(side="right", padx=5)

    def refresh_prompts(self, prompts, on_use):
        for w in self._prompts_frame.winfo_children():
            w.destroy()
        if not prompts:
            ctk.CTkLabel(self._prompts_frame, text="Sin prompts guardados", text_color="gray").pack(pady=20)
            return
        for p in prompts:
            f = ctk.CTkFrame(self._prompts_frame, fg_color="gray20")
            f.pack(fill="x", pady=2)
            title = p[1][:25] + "..." if len(p[1]) > 25 else p[1]
            ctk.CTkLabel(f, text=title, anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            ctk.CTkButton(f, text="📋", width=25, command=lambda c=p[2]: on_use(c)).pack(side="right", padx=5)

    def refresh_mini_dash(self, agents):
        for w in self._dash_frame.winfo_children():
            w.destroy()
        if not agents:
            ctk.CTkLabel(self._dash_frame, text="Sin agentes activos", text_color="gray").pack(pady=20)
            return
        for a in agents[:3]:
            ctk.CTkLabel(self._dash_frame, text=f"{a[5]} {a[1]}: {a[6]:.0f} pts").pack(anchor="w", padx=10)