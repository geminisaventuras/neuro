# @build: 2026-07-05.23-00-00 | id: ARCH-109-A | desc: Base de datos completa con agentes globales, contextos RAG y sesiones
import sqlite3, os
from datetime import datetime
from cryptography.fernet import Fernet
try:
    from cryptography.fernet import InvalidToken
except ImportError:
    from cryptography.exceptions import InvalidToken

class NeuroDatabase:
    def __init__(self, db_path="neuro_swarm.db"):
        self.db_path = db_path
        self.key_file = ".neuro_key"
        self._init_key()
        self._init_db()

    def _init_key(self):
        if not os.path.exists(self.key_file):
            with open(self.key_file, "wb") as f: f.write(Fernet.generate_key())
        with open(self.key_file, "rb") as f: self.cipher = Fernet(f.read())

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, name TEXT, provider TEXT, api_key_enc BLOB, 
            model_name TEXT, role TEXT, emoji TEXT, priority_score REAL DEFAULT 1000.0, success_count INTEGER DEFAULT 0, 
            fail_count INTEGER DEFAULT 0, avg_latency_ms REAL DEFAULT 0.0, is_active BOOLEAN DEFAULT 1, base_url TEXT DEFAULT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )''')
        try: c.execute("ALTER TABLE nodes ADD COLUMN base_url TEXT DEFAULT NULL")
        except: pass 
        c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER, prompt TEXT, response TEXT, success BOOLEAN, latency_ms REAL, rating INTEGER DEFAULT 0, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS prompt_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, category TEXT DEFAULT 'custom', is_system BOOLEAN DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content TEXT, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config (key_name TEXT PRIMARY KEY, value_data BLOB)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(project_id) REFERENCES projects(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, ia_name TEXT,
            content TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(session_id) REFERENCES sessions(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS global_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, provider TEXT, api_key_enc BLOB, 
            model_name TEXT, role TEXT, emoji TEXT, priority_score REAL DEFAULT 1000.0, 
            success_count INTEGER DEFAULT 0, fail_count INTEGER DEFAULT 0, avg_latency_ms REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1, base_url TEXT DEFAULT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS project_agents (
            project_id INTEGER, agent_id INTEGER, is_enabled BOOLEAN DEFAULT 1, individual_role TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id), FOREIGN KEY(agent_id) REFERENCES global_agents(id),
            PRIMARY KEY (project_id, agent_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS rag_contexts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL CHECK(level IN ('global','project','agent','group')),
            project_id INTEGER, agent_id INTEGER, group_id INTEGER, content TEXT, is_enabled BOOLEAN DEFAULT 1
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS agent_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, context_docs TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER, agent_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES agent_groups(id),
            FOREIGN KEY(agent_id) REFERENCES global_agents(id),
            PRIMARY KEY (group_id, agent_id)
        )''')
        # Migrar nodos existentes a global_agents
        try:
            if c.execute("SELECT COUNT(*) FROM global_agents").fetchone()[0] == 0:
                c.execute("INSERT INTO global_agents SELECT id, name, provider, api_key_enc, model_name, role, emoji, priority_score, success_count, fail_count, avg_latency_ms, is_active, base_url FROM nodes WHERE is_active=1")
                for row in c.execute("SELECT id, project_id FROM nodes WHERE is_active=1"):
                    c.execute("INSERT OR IGNORE INTO project_agents (project_id, agent_id, is_enabled) VALUES (?,?,1)", (row[1], row[0]))
            conn.commit()
        except: pass
        c.execute("INSERT OR IGNORE INTO projects (id, name) VALUES (1, 'Default Project')")
        conn.commit(); conn.close()

    def save_config(self, k, v, encrypt=False):
        conn = sqlite3.connect(self.db_path); val = self.cipher.encrypt(v.encode()) if encrypt else v.encode()
        conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (k, val)); conn.commit(); conn.close()

    def get_config(self, k, decrypt=False):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT value_data FROM config WHERE key_name=?", (k,)).fetchone(); conn.close()
        if r and r[0]:
            try: return self.cipher.decrypt(r[0]).decode() if decrypt else r[0].decode()
            except InvalidToken: return ""
        return ""

    def get_projects(self):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, name FROM projects ORDER BY id").fetchall(); conn.close(); return r

    def add_project(self, name):
        conn = sqlite3.connect(self.db_path)
        try: conn.execute("INSERT INTO projects (name) VALUES (?)", (name,)); conn.commit()
        except: pass; conn.close()

    def get_all_global_agents(self):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, name, provider, model_name, role, emoji, priority_score, success_count, fail_count, avg_latency_ms, base_url FROM global_agents WHERE is_active=1 ORDER BY priority_score DESC").fetchall(); conn.close(); return r

    def get_global_agent_by_id(self, aid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, name, provider, model_name, role, emoji, priority_score, success_count, fail_count, avg_latency_ms, base_url FROM global_agents WHERE id=?", (aid,)).fetchone(); conn.close(); return r

    def add_global_agent(self, name, provider, key, model, role, emoji, base_url=None):
        conn = sqlite3.connect(self.db_path); enc = self.cipher.encrypt(key.encode())
        conn.execute("INSERT INTO global_agents (name, provider, api_key_enc, model_name, role, emoji, base_url) VALUES (?,?,?,?,?,?,?)", (name, provider, enc, model, role, emoji, base_url))
        aid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]; conn.commit(); conn.close(); return aid

    def update_global_agent(self, aid, name, provider, key, model, role, emoji, base_url=None):
        conn = sqlite3.connect(self.db_path)
        try:
            if key and not key.startswith("gAAAAA"):
                enc = self.cipher.encrypt(key.encode())
                conn.execute("UPDATE global_agents SET name=?,provider=?,api_key_enc=?,model_name=?,role=?,emoji=?,base_url=? WHERE id=?", (name, provider, enc, model, role, emoji, base_url, aid))
            else: conn.execute("UPDATE global_agents SET name=?,provider=?,model_name=?,role=?,emoji=?,base_url=? WHERE id=?", (name, provider, model, role, emoji, base_url, aid))
            conn.commit()
        except Exception as e: print(e)
        finally: conn.close()

    def delete_global_agent(self, aid):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM project_agents WHERE agent_id=?", (aid,)); conn.execute("DELETE FROM group_members WHERE agent_id=?", (aid,))
        conn.execute("DELETE FROM global_agents WHERE id=?", (aid,)); conn.commit(); conn.close()

    def get_agent_key(self, aid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT api_key_enc FROM global_agents WHERE id=?", (aid,)).fetchone(); conn.close()
        if r and r[0] is not None:
            try: return self.cipher.decrypt(r[0]).decode().strip()
            except InvalidToken: raise ValueError("Llave maestra corrupta.")
        return None

    def update_agent_stats(self, aid, success, lat):
        conn = sqlite3.connect(self.db_path); c = conn.cursor()
        c.execute("SELECT success_count, fail_count, avg_latency_ms, priority_score FROM global_agents WHERE id=?", (aid,)); row = c.fetchone()
        if not row: return
        s, f, avg, score = row
        if success: s += 1; score += 50
        else: f += 1; score -= 100
        total = s + f; new_avg = ((avg * (total-1)) + lat) / total if total > 1 else lat
        c.execute("UPDATE global_agents SET success_count=?, fail_count=?, avg_latency_ms=?, priority_score=? WHERE id=?", (s, f, new_avg, score, aid)); conn.commit(); conn.close()

    def enable_agent_for_project(self, pid, aid, enabled=True, ind_role=None):
        conn = sqlite3.connect(self.db_path); conn.execute("INSERT OR REPLACE INTO project_agents VALUES (?,?,?,?)", (pid, aid, enabled, ind_role)); conn.commit(); conn.close()

    def get_project_agents(self, pid):
        conn = sqlite3.connect(self.db_path)
        r = conn.execute('''SELECT ga.id, ga.name, ga.provider, ga.model_name, COALESCE(pa.individual_role, ga.role), ga.emoji, ga.priority_score, ga.success_count, ga.fail_count, ga.avg_latency_ms, ga.base_url FROM global_agents ga JOIN project_agents pa ON ga.id=pa.agent_id WHERE pa.project_id=? AND pa.is_enabled=1 AND ga.is_active=1 ORDER BY ga.priority_score DESC''', (pid,)).fetchall(); conn.close(); return r

    def copy_agents_to_project(self, src, dst):
        conn = sqlite3.connect(self.db_path)
        for a in conn.execute("SELECT agent_id, individual_role FROM project_agents WHERE project_id=?", (src,)).fetchall():
            conn.execute("INSERT OR IGNORE INTO project_agents VALUES (?,?,1,?)", (dst, a[0], a[1]))
        conn.commit(); conn.close()

    def set_rag_context(self, level, content, project_id=None, agent_id=None):
        conn = sqlite3.connect(self.db_path)
        if level == 'global': conn.execute("UPDATE rag_contexts SET is_enabled=0 WHERE level='global'")
        elif level == 'project' and project_id: conn.execute("UPDATE rag_contexts SET is_enabled=0 WHERE level='project' AND project_id=?", (project_id,))
        elif level == 'agent' and agent_id: conn.execute("UPDATE rag_contexts SET is_enabled=0 WHERE level='agent' AND agent_id=?", (agent_id,))
        conn.execute("INSERT INTO rag_contexts (level, project_id, agent_id, content, is_enabled) VALUES (?,?,?,?,1)", (level, project_id, agent_id, content))
        conn.commit(); conn.close()

    def get_rag_contexts(self, project_id=None, agent_id=None):
        conn = sqlite3.connect(self.db_path); q = "SELECT level, content FROM rag_contexts WHERE is_enabled=1"; params = []
        if project_id: q += " AND (project_id=? OR project_id IS NULL)"; params.append(project_id)
        if agent_id: q += " AND (agent_id=? OR agent_id IS NULL)"; params.append(agent_id)
        r = conn.execute(q, params).fetchall(); conn.close(); return r

    def add_document(self, fn, content):
        conn = sqlite3.connect(self.db_path); conn.execute("INSERT INTO documents (filename, content) VALUES (?,?)", (fn, content)); conn.commit(); conn.close()

    def delete_document(self, did):
        conn = sqlite3.connect(self.db_path); conn.execute("DELETE FROM documents WHERE id=?", (did,)); conn.commit(); conn.close()

    def get_documents(self):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, filename FROM documents").fetchall(); conn.close(); return r

    def get_document_content(self, did):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT content FROM documents WHERE id=?", (did,)).fetchone(); conn.close(); return r[0] if r else ""

    def create_session(self, pid, title=None):
        conn = sqlite3.connect(self.db_path)
        if not title: title = datetime.now().strftime("Sesión %Y-%m-%d %H:%M")
        conn.execute("INSERT INTO sessions (project_id, title) VALUES (?,?)", (pid, title)); sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]; conn.commit(); conn.close(); return sid

    def add_message(self, sid, role, content, ia=None):
        conn = sqlite3.connect(self.db_path); conn.execute("INSERT INTO messages (session_id, role, ia_name, content) VALUES (?,?,?,?)", (sid, role, ia, content)); conn.commit(); conn.close()

    def get_session_messages(self, sid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT role, ia_name, content FROM messages WHERE session_id=? ORDER BY timestamp", (sid,)).fetchall(); conn.close()
        return [{"role": r[0], "ia_name": r[1], "content": r[2]} for r in r]

    def get_sessions(self, pid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, title FROM sessions WHERE project_id=? ORDER BY created_at DESC", (pid,)).fetchall(); conn.close(); return r

    def get_prompt_vault(self):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, title, content, category FROM prompt_vault").fetchall(); conn.close(); return r

    def add_prompt_to_vault(self, title, content, cat="custom"):
        conn = sqlite3.connect(self.db_path); conn.execute("INSERT INTO prompt_vault (title, content, category) VALUES (?,?,?)", (title, content, cat)); conn.commit(); conn.close()

    def log_interaction(self, nid, prompt, resp, success, lat, rating=0):
        conn = sqlite3.connect(self.db_path); c = conn.cursor()
        c.execute("INSERT INTO logs (node_id, prompt, response, success, latency_ms, rating) VALUES (?,?,?,?,?,?)", (nid, prompt, resp, success, lat, rating))
        lid = c.lastrowid; conn.commit(); conn.close(); return lid

    def update_log_rating(self, lid, rating):
        conn = sqlite3.connect(self.db_path); conn.execute("UPDATE logs SET rating=? WHERE id=?", (rating, lid)); conn.commit(); conn.close()

    def rate_node(self, aid, stars):
        conn = sqlite3.connect(self.db_path); conn.execute("UPDATE global_agents SET priority_score = priority_score + ? WHERE id=?", ((stars-3)*150, aid)); conn.commit(); conn.close()

    def get_node_key(self, nid): return self.get_agent_key(nid)
    def update_node_stats(self, nid, s, l): self.update_agent_stats(nid, s, l)

    # Grupos
    def create_agent_group(self, name, role, context_docs=""):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO agent_groups (name, role, context_docs) VALUES (?,?,?)", (name, role, context_docs))
        gid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]; conn.commit(); conn.close(); return gid

    def add_agent_to_group(self, gid, aid):
        conn = sqlite3.connect(self.db_path); conn.execute("INSERT OR IGNORE INTO group_members VALUES (?,?)", (gid, aid)); conn.commit(); conn.close()

    def get_agent_groups(self):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT id, name, role, context_docs FROM agent_groups").fetchall(); conn.close(); return r

    def get_group_members(self, gid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT ga.id, ga.name FROM global_agents ga JOIN group_members gm ON ga.id=gm.agent_id WHERE gm.group_id=?", (gid,)).fetchall(); conn.close(); return r

    def get_agent_groups_for_agent(self, aid):
        conn = sqlite3.connect(self.db_path); r = conn.execute("SELECT g.id, g.name, g.role, g.context_docs FROM agent_groups g JOIN group_members gm ON g.id=gm.group_id WHERE gm.agent_id=?", (aid,)).fetchall(); conn.close(); return r
