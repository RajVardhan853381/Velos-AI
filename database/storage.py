"""
Database Storage for Velos
SQLite-based audit logging for full traceability.
"""

import sqlite3
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.logger import db_logger


class AuditLog:
    """
    SQLite database for audit logging.
    Tracks all candidate verifications and agent decisions.
    """
    
    def __init__(self, db_path: str = "velos_audit.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        # Candidates table - stores overall candidate status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'PENDING',
                years_exp REAL DEFAULT 0,
                match_score INTEGER DEFAULT 0,
                authenticity_score REAL DEFAULT 0,
                final_decision TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit trail - detailed log of all agent actions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                decision TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
            )
        ''')
        
        # Verification results - summary of each verification
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                agent_1_status TEXT,
                agent_1_reason TEXT,
                agent_1_years REAL,
                agent_2_status TEXT,
                agent_2_score INTEGER,
                agent_2_reason TEXT,
                agent_3_status TEXT,
                agent_3_authenticity REAL,
                agent_3_reason TEXT,
                final_status TEXT,
                final_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
            )
        ''')
        
        # Bias flags - record all detected bias indicators
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bias_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                bias_type TEXT NOT NULL,
                description TEXT,
                action_taken TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
            )
        ''')
        
        # PII redactions - track what was redacted
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pii_redactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                redaction_type TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
            )
        ''')
        
        self.conn.commit()
    
    def save_candidate(self, candidate_id: str, initial_status: str = "PENDING") -> int:
        """Create or get candidate record"""
        if self.conn is None:
            return -1
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO candidates (candidate_id, status)
                VALUES (?, ?)
                ON CONFLICT(candidate_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP
            ''', (candidate_id, initial_status))
            self.conn.commit()
            return cursor.lastrowid or -1
        except Exception as e:
            db_logger.error(f"Error saving candidate: {e}")
            return -1
    
    def update_candidate(self, candidate_id: str, updates: Dict) -> bool:
        """Update candidate record with new data"""
        if self.conn is None:
            return False
        cursor = self.conn.cursor()
        
        allowed_fields = ['status', 'years_exp', 'match_score', 
                         'authenticity_score', 'final_decision']
        
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(candidate_id)
        
        try:
            cursor.execute(f'''
                UPDATE candidates 
                SET {', '.join(set_clauses)}
                WHERE candidate_id = ?
            ''', values)
            self.conn.commit()
            return True
        except Exception as e:
            db_logger.error(f"Error updating candidate: {e}")
            return False
    
    def save_audit_entry(self, candidate_id: str, audit_entry: Dict) -> int:
        """Save individual agent audit log entry"""
        if self.conn is None:
            return -1
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO audit_trail 
                (candidate_id, agent_name, action, decision, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                candidate_id,
                audit_entry.get('agent', 'UNKNOWN'),
                audit_entry.get('action', ''),
                audit_entry.get('decision', ''),
                audit_entry.get('timestamp', datetime.now().isoformat()),
                json.dumps(audit_entry)
            ))
            self.conn.commit()
            return cursor.lastrowid or -1
        except Exception as e:
            db_logger.error(f"Error saving audit entry: {e}")
            return -1
    
    def save_verification_result(self, candidate_id: str, result: Dict) -> int:
        """Save complete verification pipeline result"""
        if self.conn is None:
            return -1
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO verification_results 
                (candidate_id, agent_1_status, agent_1_reason, agent_1_years,
                 agent_2_status, agent_2_score, agent_2_reason,
                 agent_3_status, agent_3_authenticity, agent_3_reason,
                 final_status, final_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_id,
                result.get('agent_1_status', ''),
                result.get('agent_1_reason', ''),
                result.get('years_exp', 0),
                result.get('agent_2_status', ''),
                result.get('agent_2_score', 0),
                result.get('agent_2_reason', ''),
                result.get('agent_3_status', ''),
                result.get('agent_3_authenticity', 0),
                result.get('agent_3_reason', ''),
                result.get('final_status', ''),
                result.get('final_reason', '')
            ))
            self.conn.commit()
            return cursor.lastrowid or -1
        except Exception as e:
            db_logger.error(f"Error saving verification result: {e}")
            return -1
    
    def save_bias_flag(self, candidate_id: str, bias_type: str, 
                       description: str, action: str = "Redacted") -> int:
        """Record detected bias indicator"""
        if self.conn is None:
            return -1
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO bias_flags 
                (candidate_id, bias_type, description, action_taken)
                VALUES (?, ?, ?, ?)
            ''', (candidate_id, bias_type, description, action))
            self.conn.commit()
            return cursor.lastrowid or -1
        except Exception as e:
            db_logger.error(f"Error saving bias flag: {e}")
            return -1
    
    def save_pii_redactions(self, candidate_id: str, 
                            redaction_stats: Dict[str, int]) -> bool:
        """Record PII redaction statistics"""
        if self.conn is None:
            return False
        cursor = self.conn.cursor()
        
        try:
            for redaction_type, count in redaction_stats.items():
                if count > 0:
                    cursor.execute('''
                        INSERT INTO pii_redactions 
                        (candidate_id, redaction_type, count)
                        VALUES (?, ?, ?)
                    ''', (candidate_id, redaction_type, count))
            self.conn.commit()
            return True
        except Exception as e:
            db_logger.error(f"Error saving PII redactions: {e}")
            return False
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        """Get candidate record"""
        if self.conn is None:
            return None
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM candidates WHERE candidate_id = ?
        ''', (candidate_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_candidate_history(self, candidate_id: str) -> List[Dict]:
        """Get full audit trail for a candidate"""
        if self.conn is None:
            return []
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_trail
            WHERE candidate_id = ?
            ORDER BY timestamp ASC
        ''', (candidate_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_verification_result(self, candidate_id: str) -> Optional[Dict]:
        """Get latest verification result for a candidate"""
        if self.conn is None:
            return None
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM verification_results
            WHERE candidate_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (candidate_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_candidates(self, limit: int = 100) -> List[Dict]:
        """Get all candidates (for God Mode dashboard)"""
        if self.conn is None:
            return []
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM candidates
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_bias_flags_summary(self) -> Dict[str, int]:
        """Get summary of bias flags by type"""
        if self.conn is None:
            return {}
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT bias_type, COUNT(*) as count
            FROM bias_flags
            GROUP BY bias_type
            ORDER BY count DESC
        ''')
        
        return {row['bias_type']: row['count'] for row in cursor.fetchall()}
    
    def get_pipeline_stats(self) -> Dict:
        """Get overall pipeline statistics"""
        if self.conn is None:
            return {
                'total_candidates': 0,
                'agent_1_pass_rate': 0,
                'agent_2_pass_rate': 0,
                'agent_3_pass_rate': 0,
                'total_approved': 0,
                'total_bias_flags': 0
            }
        cursor = self.conn.cursor()
        
        stats: Dict[str, Any] = {}
        
        # Total candidates
        cursor.execute('SELECT COUNT(*) FROM candidates')
        stats['total_candidates'] = cursor.fetchone()[0]
        
        # Pass rates by agent
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN agent_1_status = 'PASS' THEN 1 ELSE 0 END) as agent_1_pass,
                SUM(CASE WHEN agent_2_status = 'PASS' THEN 1 ELSE 0 END) as agent_2_pass,
                SUM(CASE WHEN agent_3_status = 'PASS' THEN 1 ELSE 0 END) as agent_3_pass,
                COUNT(*) as total
            FROM verification_results
        ''')
        row = cursor.fetchone()
        if row and row[3] > 0:
            stats['agent_1_pass_rate'] = round(row[0] / row[3] * 100, 1) if row[0] else 0
            stats['agent_2_pass_rate'] = round(row[1] / row[3] * 100, 1) if row[1] else 0
            stats['agent_3_pass_rate'] = round(row[2] / row[3] * 100, 1) if row[2] else 0
        else:
            stats['agent_1_pass_rate'] = 0
            stats['agent_2_pass_rate'] = 0
            stats['agent_3_pass_rate'] = 0
        
        # Final approvals
        cursor.execute('''
            SELECT COUNT(*) FROM verification_results 
            WHERE final_status LIKE '%APPROVED%'
        ''')
        stats['total_approved'] = cursor.fetchone()[0]
        
        # Total bias flags
        cursor.execute('SELECT COUNT(*) FROM bias_flags')
        stats['total_bias_flags'] = cursor.fetchone()[0]
        
        return stats
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent verification decisions"""
        if self.conn is None:
            return []
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT c.candidate_id, c.status, c.final_decision,
                   v.agent_1_status, v.agent_2_score, v.agent_3_authenticity,
                   v.final_status, v.created_at
            FROM candidates c
            LEFT JOIN verification_results v ON c.candidate_id = v.candidate_id
            ORDER BY c.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Quick test
if __name__ == "__main__":
    db = AuditLog("test_audit.db")
    
    # Test saving a candidate
    candidate_id = "CAND-TEST1234"
    db.save_candidate(candidate_id)
    
    # Test audit entry
    db.save_audit_entry(candidate_id, {
        "agent": "BlindGatekeeper",
        "action": "Processing resume",
        "decision": "APPROVED",
        "years_extracted": 3.5
    })
    
    # Test verification result
    db.save_verification_result(candidate_id, {
        "agent_1_status": "PASS",
        "agent_1_reason": "3.5 years experience",
        "years_exp": 3.5,
        "agent_2_status": "PASS",
        "agent_2_score": 85,
        "final_status": "APPROVED"
    })
    
    # Test bias flag
    db.save_bias_flag(candidate_id, "gender", "Pronoun detected", "Redacted")
    
    # Get stats
    print("\nPipeline Stats:")
    print(db.get_pipeline_stats())
    
    print("\nBias Flags Summary:")
    print(db.get_bias_flags_summary())
    
    print("\nCandidate History:")
    print(db.get_candidate_history(candidate_id))
    
    db.close()
    
    # Cleanup test file
    import os
    os.remove("test_audit.db")
    print("\n✅ Database test passed!")
