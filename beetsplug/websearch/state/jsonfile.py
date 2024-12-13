import os, json, tempfile, threading
from datetime import datetime, timezone
from beetsplug.websearch.state import Repository


class JSONFileRepository(Repository):

    def __init__(self, filepath: str):
        self._lock = threading.Lock()
        self._filepath = filepath
        if not os.path.exists(filepath):
            self._state = {}
            self._save_state()
        else:
            self._load_state()

    def list(self):
        with self._lock:
            self._load_state()
            return [item for item in self._state.values()]

    def get(self, id):
        with self._lock:
            self._load_state()
            return self._state.get(id)

    def create(self, obj):
        with self._lock:
            self._load_state()
            id = obj.get('id')
            if not id:
                raise Exception('object does not specify id')
            if id in self._state:
                raise KeyError(f"object with ID '{id}' already exists")
            obj['created'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._state[id] = obj
            self._save_state()

    def update(self, obj):
        with self._lock:
            self._load_state()
            id = obj.get('id')
            if not id:
                raise Exception('object does not specify id')
            existing = self._state.get(id)
            if not existing:
                raise KeyError(f"object with ID '{id}' does not exist")
            obj['created'] = existing['created']
            # TODO: implement optimistic locking
            self._state[id] = obj
            self._save_state()

    def delete(self, id):
        with self._lock:
            self._load_state()
            if id not in self._state:
                raise KeyError(f"object with ID '{id}' does not exist")
            del self._state[id]
            self._save_state()

    def _load_state(self):
        with open(self._filepath, encoding='utf-8') as f:
            self._state = json.load(f)

    def _save_state(self):
        dir = os.path.dirname(self._filepath)
        f = tempfile.NamedTemporaryFile(dir=dir, delete=False)
        try:
            s = json.dumps(self._state)
            f.write(s.encode('utf-8'))
            f.close()
            os.replace(f.name, self._filepath)
        finally:
            f.close()
            try:
                os.unlink(f.name)
            except:
                pass
