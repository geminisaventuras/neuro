# @build: 2026-07-06.10-00-00 | id: GUI-106 | desc: Chat con exportación a Markdown, botón detener y razonamiento nativo
import customtkinter as ctk
import threading, re, os
from datetime import datetime
from tkinter import filedialog
from gui.widgets import UserBubble, ThinkingBlock, IAResponse, MessageBubble, IterationMarker
from core.orchestrator import CancelledException
from core.code_executor import CodeExecutor

class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, db, orchestrator, ui_queue, on_session_updated, on_status_change, get_project_id, **kwargs):
        super().__init__(master, fg_color="#121212", **kwargs)
        self.db = db
        self.orchestrator = orchestrator
        self.ui_queue = ui_queue
        self.on_session_updated = on_session_updated
        self.on_status_change = on_status_change
        self.get_project_id = get_project_id
        self.cancel_event = threading.Event()
        self.session_messages = []
        self.current_session_id = None
        self.current_thinking_block = None
        self._popover_active = None
        self.agent_mapping = {}

        # Área de chat
        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color="#121212", label_text="")
        self.chat_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Barra inferior flotante
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=28)
        self.bottom_frame.pack(side="bottom", fill="x", padx=30, pady=15)
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        # Icono selector de IA
        self.agent_selector_var = ctk.StringVar(value="[Enjambre Automático]")
        self.agent_selector_btn = ctk.CTkButton(self.bottom_frame, text="⚙", width=30, corner_radius=20,
                                                fg_color="transparent", text_color="#888888",
                                                hover_color="#333333", command=self._toggle_agent_popover)
        self.agent_selector_btn.grid(row=0, column=0, padx=(10, 0), pady=8, sticky="w")

        # Botón adjuntar
        self.attach_btn = ctk.CTkButton(self.bottom_frame, text="📎", width=36, height=36, corner_radius=20,
                                        fg_color="transparent", text_color="#888888", hover_color="#333333",
                                        command=self.attach_files)
        self.attach_btn.grid(row=0, column=0, padx=(45, 5), pady=8, sticky="w")

        # Botón exportar chat
        self.export_btn = ctk.CTkButton(self.bottom_frame, text="📥", width=36, height=36, corner_radius=20,
                                        fg_color="transparent", text_color="#888888", hover_color="#333333",
                                        command=self.export_chat)
        self.export_btn.grid(row=0, column=0, padx=(85, 5), pady=8, sticky="w")

        # Campo de texto flotante
        self.input_txt = ctk.CTkTextbox(self.bottom_frame, height=40, font=("Segoe UI", 13),
                                        fg_color="#2a2a2a", text_color="#e0e0e0", corner_radius=24, border_width=0)
        self.input_txt.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        self.input_txt.insert("0.0", "Escribe tu instrucción aquí...")
        self.input_txt.bind("<FocusIn>", self._clear_placeholder)
        self.input_txt.bind("<FocusOut>", self._restore_placeholder)
        self.input_txt.bind("<Return>", self._on_enter)

        # Botón enviar
        self.send_btn = ctk.CTkButton(self.bottom_frame, text="➤", width=36, height=36,
                                      corner_radius=18, fg_color="#2ecc71", hover_color="#27ae60",
                                      command=self.run_thread)
        self.send_btn.grid(row=0, column=2, padx=10, pady=8, sticky="e")

        # Botón detener
        self.stop_btn = ctk.CTkButton(self.bottom_frame, text="⏹", width=36, height=36,
                                      corner_radius=18, fg_color="#e74c3c", hover_color="#c0392b",
                                      command=self.stop_generation)

        self._highlight_selected_agent(None)

    def set_agent_list(self, mapping):
        self.agent_mapping = mapping
        self._highlight_selected_agent(None)

    def _toggle_agent_popover(self):
        if self._popover_active and self._popover_active.winfo_exists():
            self._popover_active.destroy()
            self._popover_active = None
            return

        pop = ctk.CTkToplevel(self)
        pop.overrideredirect(True)
        num_items = 1 + len(self.agent_mapping)
        pop.geometry(f"200x{30 + num_items*30}+{self.bottom_frame.winfo_rootx()+10}+{self.bottom_frame.winfo_rooty() - (30 + num_items*30)}")
        pop.configure(fg_color="#1e1e1e")

        def select_agent(name, aid=None):
            self.agent_selector_var.set(name)
            self._highlight_selected_agent(aid)
            pop.destroy()
            self._popover_active = None

        ctk.CTkButton(pop, text="[Enjambre Automático]", anchor="w", fg_color="transparent",
                      text_color="#888888", hover_color="#333333",
                      command=lambda: select_agent("[Enjambre Automático]", None)).pack(fill="x", padx=5, pady=2)
        for name, aid in self.agent_mapping.items():
            ctk.CTkButton(pop, text=name, anchor="w", fg_color="transparent",
                          text_color="#888888", hover_color="#333333",
                          command=lambda n=name, a=aid: select_agent(n, a)).pack(fill="x", padx=5, pady=2)

        self._popover_active = pop

    def _highlight_selected_agent(self, agent_id):
        for aid in self.agent_mapping.values():
            if aid == agent_id:
                self.on_status_change(aid, "selected")
            else:
                self.on_status_change(aid, "active")

    def _clear_placeholder(self, event):
        if self.input_txt.get("0.0", "end-1c").strip() == "Escribe tu instrucción aquí...":
            self.input_txt.delete("0.0", "end")

    def _restore_placeholder(self, event):
        if not self.input_txt.get("0.0", "end-1c").strip():
            self.input_txt.insert("0.0", "Escribe tu instrucción aquí...")

    def _on_enter(self, event):
        if event.state & 0x1: return
        self.run_thread()
        return "break"

    def attach_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("All files", "*.*")])
        count = 0
        for path in paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.db.add_document(os.path.basename(path), content)
                count += 1
            except: pass
        if count > 0:
            self.ui_queue.put(("toast", f"{count} archivo(s) cargado(s)"))
            self.on_session_updated()

    def export_chat(self):
        if not self.session_messages:
            self.ui_queue.put(("toast", "No hay conversación para exportar"))
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md")],
            initialfile=f"chat_neuroswarm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Chat de Neuro-Swarm – {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for msg in self.session_messages:
                    if msg["role"] == "user":
                        f.write(f"### 👤 Tú\n\n{msg['content']}\n\n")
                    elif msg["role"] == "ia":
                        name = msg.get("ia_name", "IA")
                        content = msg["content"]
                        # Extraer razonamiento si existe
                        thinking_match = re.search(r"\[RAZONAMIENTO\](.*?)\[/RAZONAMIENTO\]", content, re.DOTALL)
                        if thinking_match:
                            thinking = thinking_match.group(1).strip()
                            remaining = re.sub(r"\[RAZONAMIENTO\].*?\[/RAZONAMIENTO\]", "", content, flags=re.DOTALL).strip()
                            f.write(f"### 🤖 {name}\n\n")
                            f.write(f"> **Razonamiento:**\n>\n> {thinking.replace(chr(10), chr(10)+'> ')}\n\n")
                            if remaining:
                                f.write(f"{remaining}\n\n")
                        else:
                            f.write(f"### 🤖 {name}\n\n{content}\n\n")
                    elif msg["role"] == "system":
                        f.write(f"### ⚡ Sistema\n\n{msg['content']}\n\n")
            self.ui_queue.put(("toast", "Chat exportado como Markdown"))
        except Exception as e:
            self.ui_queue.put(("toast", f"Error al exportar: {e}"))

    def run_thread(self):
        self.cancel_event.clear()
        self.send_btn.grid_remove()
        self.stop_btn.grid(row=0, column=2, padx=10, pady=8, sticky="e")
        threading.Thread(target=self._run_task, daemon=True).start()

    def stop_generation(self):
        self.cancel_event.set()
        self._remove_thinking()
        self._add_bubble("system", "🛑 Operación cancelada por el usuario.")
        self.stop_btn.grid_remove()
        self.send_btn.grid(row=0, column=2, padx=10, pady=8, sticky="e")

    def _show_thinking(self, text):
        if self.current_thinking_block:
            self.current_thinking_block.set_content(text)
        else:
            self.current_thinking_block = ThinkingBlock(self.chat_scroll, text, collapsed=False)

    def _remove_thinking(self):
        if self.current_thinking_block:
            self.current_thinking_block.destroy()
            self.current_thinking_block = None

    def _run_task(self):
        prompt = self.input_txt.get("0.0", "end-1c")
        if prompt == "Escribe tu instrucción aquí...": prompt = ""
        if not prompt.strip():
            self.stop_btn.grid_remove()
            self.send_btn.grid(row=0, column=2, padx=10, pady=8, sticky="e")
            return

        self.input_txt.delete("0.0", "end")
        self.input_txt.insert("0.0", "Escribe tu instrucción aquí...")

        self._add_bubble("user", prompt)
        self.session_messages.append({"role":"user","content":prompt})
        if self.current_session_id:
            self.db.add_message(self.current_session_id, "user", prompt)

        ctx = ""
        docs = self.db.get_documents()
        if docs:
            parts = [f"[DOCUMENTO: {d[1]}]\n{self.db.get_document_content(d[0])}" for d in docs]
            if parts: ctx = "\n\n".join(parts) + "\n\n"

        history = ""
        for m in self.session_messages[-10:]:
            role_text = "👤" if m["role"]=="user" else f"🤖 {m.get('ia_name','IA')}"
            history += f"{role_text}: {m['content']}\n"
        if history: ctx += "HISTORIAL:\n" + history + "\n\n"

        selected = self.agent_selector_var.get()
        target_id = self.agent_mapping.get(selected) if selected != "[Enjambre Automático]" else None
        pid = self.get_project_id()

        def status_callback(agent_id, status):
            self.after(0, lambda: self.on_status_change(agent_id, status))
        def message_callback(text):
            self.after(0, lambda: self._show_thinking(text))

        try:
            success, res, name, log_id = self.orchestrator.generate(
                pid, prompt, ctx, self.ui_queue,
                target_node_id=target_id, cancel_event=self.cancel_event,
                status_callback=status_callback,
                message_callback=message_callback
            )
            if success:
                self._remove_thinking()
                self._add_bubble("ia", res, name, log_id)
                self.session_messages.append({"role":"ia","content":res,"ia_name":name})
                if self.current_session_id:
                    self.db.add_message(self.current_session_id, "ia", res, name)
                self._add_iteration_marker()
            else:
                self._remove_thinking()
                self._add_bubble("system", "❌ La generación falló en todos los agentes.")
        except CancelledException:
            self._remove_thinking()
            self._add_bubble("system", "🛑 Operación cancelada por el usuario.")
        finally:
            self.stop_btn.grid_remove()
            self.send_btn.grid(row=0, column=2, padx=10, pady=8, sticky="e")

    def _add_bubble(self, role, content, ia_name=None, log_id=None):
        if role == "user":
            UserBubble(self.chat_scroll, content,
                       on_copy=lambda txt: [self.clipboard_clear(), self.clipboard_append(txt), self.ui_queue.put(("toast","Copiado"))],
                       on_save=lambda txt: self._save_prompt(txt))
        elif role == "system":
            MessageBubble(self.chat_scroll, role, content, ia_name, log_id,
                          on_copy=lambda txt: [self.clipboard_clear(), self.clipboard_append(txt), self.ui_queue.put(("toast","Copiado"))])
        else:
            thinking_match = re.search(r"\[RAZONAMIENTO\](.*?)\[/RAZONAMIENTO\]", content, re.DOTALL)
            if thinking_match:
                thinking_text = thinking_match.group(1).strip()
                remaining = re.sub(r"\[RAZONAMIENTO\].*?\[/RAZONAMIENTO\]", "", content, flags=re.DOTALL).strip()
                ThinkingBlock(self.chat_scroll, thinking_text, collapsed=True)
                if remaining:
                    IAResponse(self.chat_scroll, remaining, ia_name, log_id,
                               on_execute=self._confirm_execute,
                               on_copy=lambda txt: [self.clipboard_clear(), self.clipboard_append(txt), self.ui_queue.put(("toast","Copiado"))],
                               on_save=lambda txt: self._save_prompt(txt),
                               on_rate=lambda r,b: [self.db.update_log_rating(b.log_id,r) if b.log_id else None,
                                                    self.ui_queue.put(("toast",f"Calificado {r}★"))])
            else:
                IAResponse(self.chat_scroll, content, ia_name, log_id,
                           on_execute=self._confirm_execute,
                           on_copy=lambda txt: [self.clipboard_clear(), self.clipboard_append(txt), self.ui_queue.put(("toast","Copiado"))],
                           on_save=lambda txt: self._save_prompt(txt),
                           on_rate=lambda r,b: [self.db.update_log_rating(b.log_id,r) if b.log_id else None,
                                                self.ui_queue.put(("toast",f"Calificado {r}★"))])
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def _add_iteration_marker(self):
        IterationMarker(self.chat_scroll)

    def _confirm_execute(self, code, lang):
        dlg = ctk.CTkToplevel(self); dlg.title("Ejecutar"); dlg.geometry("600x400"); dlg.transient(self); dlg.grab_set()
        txt = ctk.CTkTextbox(dlg, font=("Consolas",11), height=200); txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0", code); txt.configure(state="disabled")
        def aprobar(): dlg.destroy(); threading.Thread(target=self._run_sandbox, args=(code,lang), daemon=True).start()
        bf = ctk.CTkFrame(dlg, fg_color="transparent"); bf.pack(pady=10)
        ctk.CTkButton(bf, text="✅ Ejecutar", command=aprobar, fg_color="#2ecc71").pack(side="left", padx=10)
        ctk.CTkButton(bf, text="❌ Cancelar", command=dlg.destroy, fg_color="#e74c3c").pack(side="left", padx=10)

    def _run_sandbox(self, code, lang):
        from core.code_executor import CodeExecutor
        executor = CodeExecutor(timeout=30)
        self.after(0, lambda: self._add_bubble("system", f"⚡ Ejecutando {lang}...", ia_name="Sandbox"))
        result = executor.execute(code, lang); executor.cleanup()
        if result["success"]: msg = f"✅ Éxito\n{result['output']}"
        else: msg = f"❌ Error\n{result['error']}"
        self.after(0, lambda: self._add_bubble("system", msg, ia_name="Sandbox"))

    def _save_prompt(self, content):
        from gui.dialogs import save_prompt_dialog
        save_prompt_dialog(self, self.db, content, lambda: [self.on_session_updated(), self.ui_queue.put(("toast","Prompt guardado"))])

    def load_messages(self, messages):
        self.session_messages = messages
        for w in self.chat_scroll.winfo_children(): w.destroy()
        self.current_thinking_block = None
        for m in messages: self._add_bubble(m["role"], m["content"], m.get("ia_name"))

    def clear(self):
        self.session_messages = []
        for w in self.chat_scroll.winfo_children(): w.destroy()
        self.current_thinking_block = None
        self._highlight_selected_agent(None)
