# @build: 2026-07-06.05-00-00 | id: MAIN-101 | desc: Flechas colapso fijas, atajos Ctrl+flechas, backup listo
import customtkinter as ctk
import threading, queue, os, time, httpx
from core.database import NeuroDatabase
from core.orchestrator import SwarmOrchestrator
from core.sync_github import GitHubSync
from gui.widgets import NodeButton
from gui.sidebar import Sidebar
from gui.toolbox import Toolbox
from gui.chat_frame import ChatFrame
from gui.dialogs import add_agent_dialog, edit_agent_dialog, rating_dialog
from openai import OpenAI

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Neuro-Swarm v5.0")
        self.geometry("1500x900")
        self.configure(fg_color="#121212")

        self.db = NeuroDatabase()
        self.orchestrator = SwarmOrchestrator(self.db)
        self.current_project_id = 1
        self.current_session_id = None
        self.ui_queue = queue.Queue()
        self.sync_agent = GitHubSync(self.db, self.ui_queue)

        self.agent_buttons = {}
        self.agent_error_count = {}
        self.sidebar_collapsed = False
        self.header_collapsed = False
        self.toolbox_collapsed = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_main_area()
        self._bind_shortcuts()
        self.refresh_agents()
        self.after(300, self._verify_all_agents)
        self.after(200, self._new_session)
        self._check_queue()

    def _bind_shortcuts(self):
        self.bind("<Control-Left>", lambda e: self._toggle_sidebar())
        self.bind("<Control-Right>", lambda e: self._toggle_toolbox())
        self.bind("<Control-Up>", lambda e: self._toggle_header())

    def _check_queue(self):
        while not self.ui_queue.empty():
            msg_type, data = self.ui_queue.get()
            if msg_type == "toast":
                self._show_toast(data)
        self.after(100, self._check_queue)

    def _show_toast(self, msg):
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.geometry(f"+{self.winfo_x() + 50}+{self.winfo_y() + self.winfo_height() - 80}")
        ctk.CTkLabel(toast, text=msg, fg_color="#2ecc71", corner_radius=8,
                     font=("Segoe UI", 12, "bold"), text_color="white").pack(padx=20, pady=10)
        toast.after(2000, toast.destroy)

    def _verify_all_agents(self):
        agents = self.db.get_project_agents(self.current_project_id)
        def check():
            for a in agents:
                aid, name, provider, model, base_url = a[0], a[1], a[2], a[3], a[10]
                self.after(0, lambda aid=aid: self._set_agent_status(aid, "thinking"))
                try:
                    key = self.db.get_agent_key(aid)
                    if not key:
                        self.after(0, lambda aid=aid: self._set_agent_status(aid, "error"))
                        continue
                    if provider == 'gemini':
                        try:
                            from google import genai
                            g = genai.Client(api_key=key)
                            g.models.list()
                        except: raise
                    else:
                        ep = {"groq":"https://api.groq.com/openai/v1",
                              "mistral":"https://api.mistral.ai/v1",
                              "cerebras":"https://api.cerebras.ai/v1",
                              "openrouter":"https://openrouter.ai/api/v1"}.get(provider, base_url or "https://api.openai.com/v1")
                        c = OpenAI(base_url=ep, api_key=key, http_client=httpx.Client(timeout=8))
                        c.models.list()
                    self.after(0, lambda aid=aid: self._set_agent_status(aid, "active"))
                except:
                    self.after(0, lambda aid=aid: self._set_agent_status(aid, "error"))
            self.ui_queue.put(("toast", "Verificación de agentes completada"))
        threading.Thread(target=check, daemon=True).start()

    def _create_header(self):
        self.header = ctk.CTkFrame(self, height=90, fg_color="#121212")
        self.header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.header.grid_propagate(False)

        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.pack(side="left", fill="y", padx=10, pady=5)
        ctk.CTkLabel(left, text="PROYECTO ACTIVO", font=("Segoe UI", 9), text_color="#888888").pack(anchor="w")
        self.proj_var = ctk.StringVar()
        self.proj_menu = ctk.CTkOptionMenu(left, variable=self.proj_var, command=self._change_project,
                                           fg_color="#1e1e1e", button_color="#2ecc71", corner_radius=8,
                                           font=("Segoe UI", 11))
        self.proj_menu.pack(pady=2)
        ctk.CTkButton(left, text="+ Nuevo Proyecto", width=130, height=25, command=self._add_project,
                      fg_color="transparent", text_color="#888888", hover_color="#2a2a2a",
                      font=("Segoe UI", 10)).pack(pady=2)
        ctk.CTkButton(left, text="+ Agregar IA", width=130, height=25,
                      command=lambda: add_agent_dialog(self, self.db, self.current_project_id, self.refresh_agents),
                      fg_color="#2ecc71", hover_color="#27ae60", corner_radius=8,
                      font=("Segoe UI", 11, "bold")).pack(pady=2)

        self.agents_frame = ctk.CTkScrollableFrame(self.header, orientation="horizontal", height=75,
                                                   fg_color="transparent")
        self.agents_frame.pack(side="left", fill="both", expand=True, padx=10)

        self._load_projects()

    def _toggle_header(self):
        if self.header_collapsed:
            self.header.grid()
        else:
            self.header.grid_remove()
        self.header_collapsed = not self.header_collapsed

    def _load_projects(self):
        projs = self.db.get_projects()
        d = {p[1]: p[0] for p in projs}
        self.proj_menu.configure(values=list(d.keys()))
        if projs:
            self.proj_var.set(projs[0][1])
            self.current_project_id = projs[0][0]

    def _change_project(self, choice):
        projs = self.db.get_projects()
        for name, pid in {p[1]: p[0] for p in projs}.items():
            if name == choice:
                self.current_project_id = pid
                break
        self.refresh_agents()
        self._new_session()
        self.after(300, self._verify_all_agents)

    def _add_project(self):
        name = ctk.CTkInputDialog(text="Nombre:", title="Nuevo Proyecto").get_input()
        if name:
            self.db.add_project(name)
            self._load_projects()
            self.proj_var.set(name)
            self._change_project(name)

    def get_project_id(self):
        return self.current_project_id

    def refresh_agents(self):
        for w in self.agents_frame.winfo_children():
            w.destroy()
        self.agent_buttons.clear()
        agents = self.db.get_project_agents(self.current_project_id)
        mapping = {}
        for a in agents:
            btn = NodeButton(self.agents_frame, a,
                             lambda d: edit_agent_dialog(self, self.db, d, self.refresh_agents),
                             status="inactive")
            btn.pack(side="left", padx=5)
            self.agent_buttons[a[0]] = btn
            mapping[f"{a[5]} {a[1]} ({a[2]})"] = a[0]
        if hasattr(self, 'chat_frame'):
            self.chat_frame.set_agent_list(mapping)
        if hasattr(self, 'sidebar'):
            self.sidebar.refresh(self.current_project_id)
        self._refresh_toolbox()

    def _set_agent_status(self, agent_id, status):
        if agent_id in self.agent_buttons:
            self.agent_buttons[agent_id].update_status(status)
            if status == "error":
                self.agent_error_count[agent_id] = self.agent_error_count.get(agent_id, 0) + 1
                if self.agent_error_count.get(agent_id, 0) >= 2:
                    self.agent_buttons[agent_id].update_status("error")
            elif status == "active":
                self.agent_error_count[agent_id] = 0

    def _create_main_area(self):
        self.tabs = ctk.CTkTabview(self, fg_color="#121212")
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        gen_tab = self.tabs.add("Generador Táctico")
        gen_tab.grid_columnconfigure(0, weight=0)
        gen_tab.grid_columnconfigure(1, weight=1)
        gen_tab.grid_columnconfigure(2, weight=0)
        gen_tab.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(gen_tab, self.db, self._load_session, self._new_session)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(5, 2), pady=5)

        self.chat_frame = ChatFrame(gen_tab, self.db, self.orchestrator, self.ui_queue,
                                    self._refresh_toolbox, self._set_agent_status, self.get_project_id)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)

        self.toolbox = Toolbox(gen_tab, self.db, on_upload=self._upload_doc)
        self.toolbox.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)

        # Flechas de colapso como hijos del gen_tab (siempre visibles)
        self.collapse_sidebar_btn = ctk.CTkButton(gen_tab, text="◀", width=18, command=self._toggle_sidebar,
                                                   fg_color="transparent", text_color="#888888")
        self.collapse_sidebar_btn.place(relx=0.0, rely=0.5, anchor="w", x=2)
        self.collapse_toolbox_btn = ctk.CTkButton(gen_tab, text="▶", width=18, command=self._toggle_toolbox,
                                                   fg_color="transparent", text_color="#888888")
        self.collapse_toolbox_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)

        self.tabs.add("Dashboard Analítico")
        self.tabs.add("Contexto RAG")
        self.tabs.add("Sincronización (GitHub)")

    def _toggle_sidebar(self):
        if self.sidebar_collapsed:
            self.sidebar.grid()
            self.collapse_sidebar_btn.configure(text="◀")
        else:
            self.sidebar.grid_remove()
            self.collapse_sidebar_btn.configure(text="▶")
        self.sidebar_collapsed = not self.sidebar_collapsed

    def _toggle_toolbox(self):
        if self.toolbox_collapsed:
            self.toolbox.grid()
            self.collapse_toolbox_btn.configure(text="▶")
        else:
            self.toolbox.grid_remove()
            self.collapse_toolbox_btn.configure(text="◀")
        self.toolbox_collapsed = not self.toolbox_collapsed

    def _new_session(self):
        if self.current_session_id and self.chat_frame.session_messages:
            last = self.orchestrator.get_last_node_id()
            if last:
                rating_dialog(self, self.db, last, self.refresh_agents)
        self.current_session_id = self.db.create_session(self.current_project_id)
        self.chat_frame.current_session_id = self.current_session_id
        self.chat_frame.clear()
        self.sidebar.refresh(self.current_project_id)

    def _load_session(self, sid):
        self.current_session_id = sid
        self.chat_frame.current_session_id = sid
        msgs = self.db.get_session_messages(sid)
        self.chat_frame.load_messages(msgs)

    def _refresh_toolbox(self):
        docs = self.db.get_documents()
        self.toolbox.refresh_docs(docs, lambda did: [self.db.delete_document(did), self._refresh_toolbox()])
        prompts = self.db.get_prompt_vault()
        self.toolbox.refresh_prompts(prompts, lambda c: [self.chat_frame.input_txt.delete("0.0", "end"),
                                                         self.chat_frame.input_txt.insert("0.0", c)])
        agents = self.db.get_project_agents(self.current_project_id)
        self.toolbox.refresh_mini_dash(agents)

    def _upload_doc(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.md *.py *.json")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.db.add_document(os.path.basename(path), f.read())
            self._refresh_toolbox()
            self.ui_queue.put(("toast", "Documento subido"))


if __name__ == "__main__":
    App().mainloop()
