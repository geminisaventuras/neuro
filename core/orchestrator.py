# @build: 2026-07-06.09-00-00 | id: ARCH-109-D | desc: Orquestador con captura de razonamiento nativo de API
import time, traceback, httpx
from openai import OpenAI
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_NEW_GENAI = True
except ImportError:
    HAS_NEW_GENAI = False

class CancelledException(Exception): pass

class SwarmOrchestrator:
    def __init__(self, db):
        self.db = db
        self.last_used_node_id = None

    def generate(self, project_id, prompt_text, context_docs="", ui_queue=None,
                 target_node_id=None, cancel_event=None,
                 status_callback=None, message_callback=None):
        if target_node_id:
            agent = self.db.get_global_agent_by_id(target_node_id)
            if not agent: return False, "Agente no existe.", None, None
            nodes = [agent]
        else:
            nodes = self.db.get_project_agents(project_id)
        if not nodes or nodes[0] is None: return False, "No hay IAs.", None, None

        # Contexto RAG multinivel
        rag_parts = []
        for lvl, content in self.db.get_rag_contexts():
            if lvl == 'global': rag_parts.append(f"[CONTEXTO GLOBAL]\n{content}")
        if project_id:
            for lvl, content in self.db.get_rag_contexts(project_id=project_id):
                if lvl == 'project': rag_parts.append(f"[CONTEXTO DEL PROYECTO]\n{content}")
        if target_node_id:
            for lvl, content in self.db.get_rag_contexts(agent_id=target_node_id):
                if lvl == 'agent': rag_parts.append(f"[CONTEXTO DE LA IA]\n{content}")
            for g in self.db.get_agent_groups_for_agent(target_node_id):
                for lvl, content in self.db.get_rag_contexts(group_id=g[0]):
                    if lvl == 'group': rag_parts.append(f"[GRUPO {g[1]}]\n{content}")

        rag = "\n\n".join(rag_parts) if rag_parts else ""
        full = rag + "\n\n" + context_docs if context_docs else rag
        if len(full) > 15000: full = full[-15000:] + "\n[Truncado]"
        if rag or context_docs: full += "\n\n[INSTRUCCIÓN]: Tienes acceso a los documentos de contexto. Úsalos."
        full_prompt = f"{full}\n\nUSER REQUEST:\n{prompt_text}"
        last_error = ""

        error_counts = {}
        for node in nodes:
            if cancel_event and cancel_event.is_set():
                raise CancelledException()
            nid, name, provider, model, role, emoji, score, s_cnt, f_cnt, lat, base_url = node

            if status_callback: status_callback(nid, "thinking")
            if message_callback: message_callback(f"🤖 {name} está generando respuesta...")

            t0 = time.time(); success = False; resp_text = ""; reasoning = ""; retries = 1
            while retries >= 0 and not success:
                if cancel_event and cancel_event.is_set():
                    if status_callback: status_callback(nid, "active")
                    raise CancelledException()
                try:
                    key = (self.db.get_agent_key(nid) or "").strip()
                    if provider in ['groq','mistral','custom','cerebras','openrouter']:
                        ep, defm = {"groq": ("https://api.groq.com/openai/v1","llama-3.1-8b-instant"),
                                    "mistral": ("https://api.mistral.ai/v1","mistral-large-latest"),
                                    "cerebras": ("https://api.cerebras.ai/v1","llama3.1-8b"),
                                    "openrouter": ("https://openrouter.ai/api/v1","openai/gpt-4o")}.get(provider, (None,None))
                        if provider == 'custom':
                            ep = (base_url or "https://api.openai.com/v1").rstrip("/").removesuffix("/chat/completions")
                            defm = model or "gpt-3.5-turbo"
                        h = {"HTTP-Referer":"http://localhost:3000","X-Title":"Neuro-Swarm"} if provider=='openrouter' else {}
                        c = OpenAI(base_url=ep, api_key=key, http_client=httpx.Client(timeout=30, follow_redirects=True), default_headers=h)
                        r = c.chat.completions.create(model=model or defm, messages=[{"role":"system","content":role or "Asistente"},{"role":"user","content":full_prompt}], temperature=0.7, max_tokens=2048)
                        # capturar razonamiento si existe
                        msg = r.choices[0].message
                        if hasattr(msg, 'reasoning_content') and msg.reasoning_content:
                            reasoning = msg.reasoning_content.strip()
                        resp_text = msg.content or ""
                        success = True
                    elif provider == 'gemini':
                        if not HAS_NEW_GENAI: raise Exception("Instala google-genai")
                        g = genai.Client(api_key=key)
                        r = g.models.generate_content(model=model or "gemini-3.5-flash", contents=full_prompt, config=genai_types.GenerateContentConfig(system_instruction=role or "Asistente"))
                        # Gemini thoughts
                        try:
                            for part in r.candidates[0].content.parts:
                                if hasattr(part, 'thought') and part.thought:
                                    reasoning += part.thought + "\n"
                            reasoning = reasoning.strip()
                        except: pass
                        resp_text = r.text
                        success = True
                    else: raise ValueError(f"Proveedor {provider}")
                except Exception as e:
                    last_error = traceback.format_exc()
                    if "429" in last_error and retries>0:
                        time.sleep(3); retries -= 1; continue
                    break
            lat = (time.time()-t0)*1000
            if success:
                self.db.update_agent_stats(nid, True, lat)
                # Combinar razonamiento y respuesta
                combined = ""
                if reasoning and not re.search(r'\[RAZONAMIENTO\]', resp_text, re.IGNORECASE):
                    combined = f"[RAZONAMIENTO]\n{reasoning}\n[/RAZONAMIENTO]\n\n{resp_text}"
                else:
                    combined = resp_text
                lid = self.db.log_interaction(nid, prompt_text, combined, True, lat)
                if status_callback: status_callback(nid, "active")
                self.last_used_node_id = nid
                return True, combined, name, lid
            else:
                error_counts[nid] = error_counts.get(nid, 0) + 1
                self.db.update_agent_stats(nid, False, lat)
                self.db.log_interaction(nid, prompt_text, last_error, False, lat)
                if error_counts[nid] >= 2:
                    if status_callback: status_callback(nid, "error")
                else:
                    if status_callback: status_callback(nid, "warning")
        return False, f"Fallo total del enjambre.\n{last_error}", None, None

    def get_last_node_id(self): return self.last_used_node_id
