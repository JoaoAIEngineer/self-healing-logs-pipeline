import sqlite3
import os

class LogAuditDB:
    def __init__(self, db_path="data/metrics_pipeline.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clean_logs (
                request_id TEXT PRIMARY KEY,
                prompt TEXT,
                response_text TEXT,
                tokens_used INTEGER,
                healed_status TEXT,  -- 'PERFECT', 'HEALED', 'FAILED'
                fixing_strategy TEXT
            );
            """)
            conn.commit()