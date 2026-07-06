# @build: 2026-07-05.23-00-00 | id: EXEC-003 | desc: Sandbox de ejecución de código
import subprocess, sys, os, tempfile, uuid, time

class CodeExecutor:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.sandbox_dir = tempfile.mkdtemp(prefix="neuro_sandbox_")

    def execute(self, code, language="python"):
        trace_id = str(uuid.uuid4()); start = time.time()
        if language not in ["python","javascript","bash"]:
            return {"success":False,"error":"Lenguaje no soportado","trace_id":trace_id}
        try:
            if language == "python": result = self._run_python(code, trace_id)
            elif language == "javascript": result = self._run_javascript(code, trace_id)
            else: result = self._run_bash(code, trace_id)
        except Exception as e: result = {"success":False,"error":str(e)}
        result["trace_id"] = trace_id
        result["execution_time_ms"] = (time.time()-start)*1000
        return result

    def _run_python(self, code, trace_id):
        fp = os.path.join(self.sandbox_dir, f"{trace_id}.py")
        with open(fp, "w", encoding="utf-8") as f:
            f.write("import sys,builtins\nBLOCKED=['subprocess','shutil','socket','requests','http','urllib']\norig=builtins.__import__\ndef safe_import(n,*a,**kw):\n    if n in BLOCKED or n.startswith('http'): raise ImportError(f'{n} blocked')\n    return orig(n,*a,**kw)\nbuiltins.__import__=safe_import\n" + code)
        try:
            proc = subprocess.run([sys.executable, fp], capture_output=True, text=True, timeout=self.timeout, cwd=self.sandbox_dir, env={**os.environ, "HOME":self.sandbox_dir})
            if proc.returncode: return {"success":False,"error":proc.stderr,"output":proc.stdout}
            return {"success":True,"output":proc.stdout,"error":None}
        except subprocess.TimeoutExpired: return {"success":False,"error":"Timeout"}
        finally:
            if os.path.exists(fp): os.remove(fp)

    def _run_javascript(self, code, trace_id):
        if not self._has_node(): return {"success":False,"error":"Node.js no instalado"}
        fp = os.path.join(self.sandbox_dir, f"{trace_id}.js")
        with open(fp,"w") as f: f.write(code)
        try:
            proc = subprocess.run(["node",fp], capture_output=True, text=True, timeout=self.timeout)
            if proc.returncode: return {"success":False,"error":proc.stderr,"output":proc.stdout}
            return {"success":True,"output":proc.stdout,"error":None}
        except subprocess.TimeoutExpired: return {"success":False,"error":"Timeout"}
        finally:
            if os.path.exists(fp): os.remove(fp)

    def _run_bash(self, code, trace_id):
        if sys.platform == "win32": return {"success":False,"error":"Bash no disponible en Windows"}
        try:
            proc = subprocess.run(["bash","-c",code], capture_output=True, text=True, timeout=self.timeout)
            if proc.returncode: return {"success":False,"error":proc.stderr,"output":proc.stdout}
            return {"success":True,"output":proc.stdout,"error":None}
        except subprocess.TimeoutExpired: return {"success":False,"error":"Timeout"}

    def _has_node(self):
        try: subprocess.run(["node","--version"], capture_output=True, timeout=5); return True
        except: return False

    def cleanup(self):
        import shutil
        if os.path.exists(self.sandbox_dir): shutil.rmtree(self.sandbox_dir, ignore_errors=True)
