# @build: 2026-07-05.23-00-00 | id: ARCH-109-D | desc: Motor GitHub Sync bidireccional
import requests, base64, os
from datetime import datetime

class GitHubSync:
    def __init__(self, db, ui_queue):
        self.db = db; self.ui_queue = ui_queue
        self.api_base = "https://api.github.com"

    def _log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        if self.ui_queue: self.ui_queue.put(("gh_log", f"[{ts}] {msg}\n"))

    def get_credentials(self):
        return self.db.get_config("github_repo"), self.db.get_config("github_token", decrypt=True)

    def list_directory(self, path=""):
        repo, token = self.get_credentials()
        if not repo or not token: self._log("Faltan credenciales"); return None
        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        self._log(f"Escaneando /{path or 'raíz'}")
        try:
            r = requests.get(url, headers=h, timeout=10)
            if r.status_code == 200: self._log("Directorio indexado"); return r.json()
            elif r.status_code == 404: self._log("Vacío o no existe"); return []
            else: self._log(f"Error HTTP {r.status_code}"); return None
        except Exception as e: self._log(f"Error conexión: {e}"); return None

    def pull_file(self, name, url):
        _, token = self.get_credentials()
        h = {"Authorization": f"Bearer {token}"}
        self._log(f"Descargando {name}")
        try:
            r = requests.get(url, headers=h, timeout=15)
            if r.status_code == 200:
                self.db.add_document(f"GH_{name}", r.text)
                self._log(f"Guardado {name}")
                self.ui_queue.put(("gh_refresh", None))
            else: self._log(f"Error HTTP {r.status_code}")
        except Exception as e: self._log(f"Error red: {e}")

    def upload_file(self, remote_path, content, msg="Carga desde Neuro-Swarm"):
        repo, token = self.get_credentials()
        if not repo or not token: self._log("Sin credenciales"); return
        url = f"{self.api_base}/repos/{repo}/contents/{remote_path}"
        h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        sha = None
        try:
            gr = requests.get(url, headers=h)
            if gr.status_code == 200: sha = gr.json().get("sha")
        except: pass
        data = {"message": msg, "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: data["sha"] = sha
        self._log(f"Subiendo {remote_path}")
        try:
            pr = requests.put(url, headers=h, json=data, timeout=20)
            if pr.status_code in [200,201]: self._log("Subida exitosa"); self.ui_queue.put(("gh_refresh", None))
            else: self._log(f"Error HTTP {pr.status_code}")
        except Exception as e: self._log(f"Error red: {e}")
