"""
Analytics Service - FINAL FIX
Track usage, engagement, and generate insights
"""

from typing import Dict, List
from datetime import datetime, timedelta
import os
import logging
from services.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Database): # <-- Receive the db instance
        self.db = db
    
    # ==================== Logging Methods ====================
    
    def log_document_processed(self, user_id: str, doc_id: str, chunks_created: int):
        """Log document processing completion"""
        self.db.log_event(
            user_id=user_id,
            event_type="document_processed",
            event_data={
                "document_id": doc_id,
                "chunks_created": chunks_created,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_chat_interaction(self, user_id: str, mode: str):
        """Log student chat interaction"""
        self.db.log_event(
            user_id=user_id,
            event_type="chat_interaction",
            event_data={
                "mode": mode,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_content_generation(self, faculty_id: str, content_type: str, num_items: int):
        """Log faculty content generation"""
        self.db.log_event(
            user_id=faculty_id,
            event_type="content_generated",
            event_data={
                "content_type": content_type,
                "num_items": num_items,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_admin_action(self, admin_id: str, action: str, target_id: str):
        """Log admin actions"""
        self.db.log_event(
            user_id=admin_id,
            event_type="admin_action",
            event_data={
                "action": action,
                "target_id": target_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # ==================== Platform Statistics ====================
    
    def get_platform_stats(self) -> Dict:
        """Get comprehensive platform statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total documents
        cursor.execute('SELECT COUNT(*) FROM documents')
        total_docs = cursor.fetchone()[0]
        
        # Completed documents
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'completed'")
        completed_docs = cursor.fetchone()[0]
        
        # Processing documents
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'processing'")
        processing_docs = cursor.fetchone()[0]
        
        # Total chat sessions
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        total_messages = cursor.fetchone()[0]
        
        # Generated content
        cursor.execute('SELECT COUNT(*) FROM generated_content')
        total_generated = cursor.fetchone()[0]
        
        # Content by type
        cursor.execute('''
            SELECT content_type, COUNT(*) as count 
            FROM generated_content 
            GROUP BY content_type
        ''')
        content_by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent activity (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM analytics_events 
            WHERE timestamp > ?
        ''', (seven_days_ago,))
        recent_activity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "documents": {
                "total": total_docs,
                "completed": completed_docs,
                "processing": processing_docs,
                "failed": total_docs - completed_docs - processing_docs
            },
            "chat": {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "avg_messages_per_session": round(total_messages / total_sessions, 2) if total_sessions > 0 else 0
            },
            "generated_content": {
                "total": total_generated,
                "by_type": content_by_type
            },
            "activity": {
                "last_7_days": recent_activity
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # ==================== Student Analytics ====================
    
    def get_student_stats(self, student_id: str) -> Dict:
        """Get engagement statistics for a student"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Chat sessions
        cursor.execute('''
            SELECT COUNT(*) FROM chat_sessions WHERE user_id = ?
        ''', (student_id,))
        total_sessions = cursor.fetchone()[0]
        
        # Messages sent
        cursor.execute('''
            SELECT COUNT(*) FROM chat_messages WHERE user_id = ?
        ''', (student_id,))
        total_messages = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM analytics_events
            WHERE user_id = ?
            GROUP BY event_type
        ''', (student_id,))
        activity_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Last active
        cursor.execute('''
            SELECT MAX(timestamp) FROM analytics_events WHERE user_id = ?
        ''', (student_id,))
        last_active = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "student_id": student_id,
            "chat_sessions": total_sessions,
            "messages_sent": total_messages,
            "activity_breakdown": activity_breakdown,
            "last_active": last_active,
            "engagement_level": self._calculate_engagement_level(total_sessions, total_messages)
        }
    
    def _calculate_engagement_level(self, sessions: int, messages: int) -> str:
        """Calculate engagement level based on activity"""
        if sessions == 0:
            return "inactive"
        elif sessions < 5 or messages < 10:
            return "low"
        elif sessions < 20 or messages < 50:
            return "medium"
        else:
            return "high"
    
    # ==================== Faculty Analytics ====================
    
    def get_faculty_stats(self, faculty_id: str) -> Dict:
        """Get content generation statistics for faculty"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Documents uploaded
        cursor.execute('''
            SELECT COUNT(*) FROM documents WHERE uploaded_by = ?
        ''', (faculty_id,))
        documents_uploaded = cursor.fetchone()[0]
        
        # Content generated
        cursor.execute('''
            SELECT content_type, COUNT(*) as count
            FROM generated_content
            WHERE faculty_id = ?
            GROUP BY content_type
        ''', (faculty_id,))
        content_generated = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total content items
        cursor.execute('''
            SELECT COUNT(*) FROM generated_content WHERE faculty_id = ?
        ''', (faculty_id,))
        total_generated = cursor.fetchone()[0]
        
        # Recent uploads
        cursor.execute('''
            SELECT filename, created_at, status
            FROM documents
            WHERE uploaded_by = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (faculty_id,))
        recent_uploads = [
            {"filename": row[0], "uploaded_at": row[1], "status": row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "faculty_id": faculty_id,
            "documents_uploaded": documents_uploaded,
            "content_generated": content_generated,
            "total_items_generated": total_generated,
            "recent_uploads": recent_uploads
        }
    
    # ==================== Document Analytics ====================
    
    def get_popular_documents(self, limit: int = 10) -> List[Dict]:
        """Get most accessed documents based on chat context"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.id,
                d.filename,
                d.uploaded_by,
                d.created_at,
                d.chunks_created,
                COUNT(cm.message_id) as access_count
            FROM documents d
            LEFT JOIN chat_messages cm ON cm.sources LIKE '%' || d.filename || '%'
            WHERE d.status = 'completed'
            GROUP BY d.id
            ORDER BY access_count DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "document_id": row[0],
                "filename": row[1],
                "uploaded_by": row[2],
                "created_at": row[3],
                "chunks_created": row[4],
                "access_count": row[5]
            }
            for row in rows
        ]
    
    # ==================== System Metrics ====================
    
    def get_storage_usage(self) -> float:
        """Calculate storage usage in MB"""
        try:
            from config import UPLOADS_DIR
            upload_dir = UPLOADS_DIR
            if not os.path.exists(upload_dir):
                return 0.0
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(upload_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            # Convert bytes to MB
            return round(total_size / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"Error calculating storage: {str(e)}")
            return 0.0
    
    def get_active_users_today(self) -> int:
        """Count users active today"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) 
            FROM analytics_events
            WHERE DATE(timestamp) = ?
        ''', (today,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    # ==================== Usage Trends ====================
    
    def get_usage_trend(self, days: int = 7) -> Dict:
        """Get daily usage trend for last N days"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as events,
                COUNT(DISTINCT user_id) as unique_users
            FROM analytics_events
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trend = [
            {
                "date": row[0],
                "events": row[1],
                "unique_users": row[2]
            }
            for row in rows
        ]
        
        return {
            "period_days": days,
            "trend": trend
        }