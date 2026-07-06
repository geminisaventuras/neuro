# @build: 2026-07-05.23-00-00 | id: GUI-104 | desc: Diálogos (Agregar/Editar IA, Calificar, Guardar Prompt)
import customtkinter as ctk
from tkinter import messagebox

def add_agent_dialog(parent, db, project_id, callback):
    dlg = ctk.CTkToplevel(parent); dlg.title("Nuevo Agente Global"); dlg.geometry("480x680"); dlg.transient(parent); dlg.grab_set()
    name_var = ctk.StringVar(); provider_var = ctk.StringVar(value="groq"); model_var = ctk.StringVar()
    key_var = ctk.StringVar(); role_var = ctk.StringVar(value="Experto."); emoji_var = ctk.StringVar(value="🤖"); burl_var = ctk.StringVar()
    ctk.CTkLabel(dlg, text="Nombre:").pack(pady=(15,0)); ctk.CTkEntry(dlg, textvariable=name_var, placeholder_text="Ej. MANTRAX").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Proveedor:").pack(pady=(10,0)); ctk.CTkOptionMenu(dlg, variable=provider_var, values=["groq","mistral","gemini","cerebras","openrouter","custom"]).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Base URL:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=burl_var, placeholder_text="https://...").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="API Key:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=key_var, show="*", placeholder_text="Clave secreta").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Modelo:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=model_var, placeholder_text="llama3.1-8b").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Rol del sistema:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=role_var, placeholder_text="Instrucción").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Emoji:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=emoji_var, placeholder_text="🤖").pack(pady=5, padx=20, fill="x")
    def save():
        aid = db.add_global_agent(name_var.get(), provider_var.get(), key_var.get(), model_var.get(), role_var.get(), emoji_var.get(), burl_var.get())
        db.enable_agent_for_project(project_id, aid); callback(); dlg.destroy()
    ctk.CTkButton(dlg, text="Guardar", command=save, fg_color="#2ecc71", height=35).pack(pady=20)

def edit_agent_dialog(parent, db, agent_data, callback):
    aid, name, provider, model, role, emoji, score, s_cnt, f_cnt, lat, base_url = agent_data
    dlg = ctk.CTkToplevel(parent); dlg.geometry("480x680"); dlg.title("Editar Agente"); dlg.transient(parent); dlg.grab_set()
    name_var = ctk.StringVar(value=name); provider_var = ctk.StringVar(value=provider)
    key_var = ctk.StringVar(value="********"); model_var = ctk.StringVar(value=model or "")
    role_var = ctk.StringVar(value=role); emoji_var = ctk.StringVar(value=emoji); burl_var = ctk.StringVar(value=base_url or "")
    ctk.CTkLabel(dlg, text="Nombre:").pack(pady=(15,0)); ctk.CTkEntry(dlg, textvariable=name_var).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Proveedor:").pack(pady=(10,0)); ctk.CTkOptionMenu(dlg, variable=provider_var, values=["groq","mistral","gemini","cerebras","openrouter","custom"]).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Base URL:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=burl_var).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="API Key:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=key_var, show="*", placeholder_text="••••••••").pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Modelo:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=model_var).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Rol:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=role_var).pack(pady=5, padx=20, fill="x")
    ctk.CTkLabel(dlg, text="Emoji:").pack(pady=(10,0)); ctk.CTkEntry(dlg, textvariable=emoji_var).pack(pady=5, padx=20, fill="x")
    def save():
        new_key = None if key_var.get()=="********" else key_var.get()
        db.update_global_agent(aid, name_var.get(), provider_var.get(), new_key, model_var.get(), role_var.get(), emoji_var.get(), burl_var.get())
        callback(); dlg.destroy()
    def delete():
        db.delete_global_agent(aid); callback(); dlg.destroy()
    btn_frame = ctk.CTkFrame(dlg, fg_color="transparent"); btn_frame.pack(pady=20)
    ctk.CTkButton(btn_frame, text="Guardar", command=save, fg_color="#2ecc71", height=35).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="Eliminar", command=delete, fg_color="#e74c3c", height=35).pack(side="left", padx=10)

def rating_dialog(parent, db, agent_id, callback):
    dlg = ctk.CTkToplevel(parent); dlg.title("Calificar IA"); dlg.geometry("300x150"); dlg.transient(parent); dlg.grab_set()
    ctk.CTkLabel(dlg, text="Califica a la IA:").pack(pady=10)
    def set_rating(stars):
        db.rate_node(agent_id, stars); callback(); dlg.destroy()
    bf = ctk.CTkFrame(dlg, fg_color="transparent"); bf.pack(pady=10)
    for i in range(1,6): ctk.CTkButton(bf, text=f"{i}★", width=30, command=lambda s=i: set_rating(s)).pack(side="left", padx=2)

def save_prompt_dialog(parent, db, content, callback):
    dlg = ctk.CTkToplevel(parent); dlg.title("Guardar Prompt"); dlg.geometry("400x200"); dlg.transient(parent); dlg.grab_set()
    ctk.CTkLabel(dlg, text="Categoría:").pack(pady=5); cat_var = ctk.StringVar(); ctk.CTkEntry(dlg, textvariable=cat_var).pack(pady=5)
    def save():
        title = content[:50].replace('\n',' ')
        db.add_prompt_to_vault(title, content, cat_var.get() or "custom"); callback(); dlg.destroy()
    ctk.CTkButton(dlg, text="Guardar", command=save).pack(pady=10)
