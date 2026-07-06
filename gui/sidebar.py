# @build: 2026-07-06.08-00-00 | id: GUI-103 | desc: Sidebar con búsqueda en contenido completo de mensajes
import customtkinter as ctk
from datetime import datetime

class Sidebar(ctk.CTkScrollableFrame):
    def __init__(self, master, db, on_load_session, on_new_session, **kwargs):
        super().__init__(master, width=220, fg_color="#121212", label_text="", **kwargs)
        self.db = db
        self.on_load_session = on_load_session
        self.on_new_session = on_new_session
        self.current_project_id = 1

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, placeholder_text="Buscar sesiones...",
                                         fg_color="#1e1e1e", corner_radius=10, height=30)
        self.search_entry.pack(fill="x", padx=8, pady=(10, 5), side="top")
        self.search_var.trace_add("write", lambda *a: self.refresh(self.current_project_id))

        self._inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._inner_frame.pack(fill="both", expand=True)

    def _format_time_relative(self, timestamp_str):
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            return "Desconocido"
        now = datetime.now()
        diff = now - dt
        if diff.days == 0: return "Hoy"
        elif diff.days == 1: return "Ayer"
        elif diff.days <= 7: return f"Hace {diff.days} días"
        elif diff.days <= 14: return "Hace 1 semana"
        else: return f"Hace {diff.days // 7} semanas"

    def _get_first_user_message(self, session_id):
        msgs = self.db.get_session_messages(session_id)
        for m in msgs:
            if m["role"] == "user":
                words = m["content"].split()
                return " ".join(words[:5]) + ("..." if len(words) > 5 else "")
        return "Sin mensajes"

    def _session_contains_text(self, session_id, query):
        """Busca la query en todos los mensajes de la sesión."""
        msgs = self.db.get_session_messages(session_id)
        for m in msgs:
            if query in m["content"].lower():
                return True
        return False

    def refresh(self, project_id):
        self.current_project_id = project_id
        for w in self._inner_frame.winfo_children():
            w.destroy()

        sessions = self.db.get_sessions(project_id)
        query = self.search_var.get().lower().strip()

        groups = {}
        for s in sessions:
            sid, title = s[0], s[1]
            created = s[2] if len(s) > 2 else ""
            first_msg = self._get_first_user_message(sid)
            if query:
                # Buscar en el título visible y en el contenido completo
                if query in first_msg.lower() or query in title.lower() or self._session_contains_text(sid, query):
                    pass
                else:
                    continue  # No coincide, omitir
            time_group = self._format_time_relative(created)
            if time_group not in groups:
                groups[time_group] = []
            groups[time_group].append((sid, first_msg, created))

        ordered_groups = []
        if "Hoy" in groups: ordered_groups.append("Hoy")
        if "Ayer" in groups: ordered_groups.append("Ayer")
        for key in groups:
            if key not in ("Hoy","Ayer"):
                ordered_groups.append(key)
        def sort_key(k):
            if k == "Hoy": return 0
            if k == "Ayer": return 1
            import re
            nums = re.findall(r'\d+', k)
            return int(nums[0]) if nums else 999
        ordered_groups.sort(key=sort_key)

        for group in ordered_groups:
            items = groups[group]
            if not items: continue
            ctk.CTkLabel(self._inner_frame, text=group, font=("Segoe UI", 10, "bold"), text_color="#888888").pack(anchor="w", padx=10, pady=(10,2))
            for sid, first_msg, _ in items:
                display = f"{first_msg[:40]}{'...' if len(first_msg)>40 else ''}" if first_msg else "Sin título"
                btn = ctk.CTkButton(self._inner_frame, text=display, anchor="w",
                                    fg_color="transparent", text_color="#aaaaaa",
                                    hover_color="#2a2a2a", corner_radius=6,
                                    font=("Segoe UI", 11), height=35,
                                    command=lambda sid=sid: self.on_load_session(sid))
                btn.pack(fill="x", pady=2, padx=5)

        ctk.CTkButton(self._inner_frame, text="+ Nueva Sesión", fg_color="#2ecc71",
                      hover_color="#27ae60", corner_radius=8,
                      font=("Segoe UI", 12, "bold"), height=35,
                      command=self.on_new_session).pack(fill="x", pady=15, padx=5)
