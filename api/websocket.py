"""
WebSocket Real-time Event Pipeline
Handles real-time violation alerts with deduplication and cooldown
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
import asyncio
import json
from datetime import datetime, timedelta

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.alert_cache: Dict[str, datetime] = {}  # For cooldown
        self.sent_alerts: Set[str] = set()  # For deduplication
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ Client disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    def should_send_alert(self, alert_id: str, cooldown_seconds: int = 60) -> bool:
        """
        Check if alert should be sent based on:
        1. Deduplication (not sent in this session)
        2. Cooldown (not sent in last N seconds)
        """
        now = datetime.now()
        
        # Check if already sent in this session
        if alert_id in self.sent_alerts:
            return False
        
        # Check cooldown
        if alert_id in self.alert_cache:
            last_sent = self.alert_cache[alert_id]
            if now - last_sent < timedelta(seconds=cooldown_seconds):
                return False
        
        # Mark as sent
        self.sent_alerts.add(alert_id)
        self.alert_cache[alert_id] = now
        return True
    
    async def send_violation_alert(self, violation: dict):
        """
        Send violation alert with rules engine
        - Deduplication
        - Cooldown
        - Severity-based routing
        """
        alert_id = f"{violation.get('worker')}_{violation.get('violation')}_{violation.get('location')}"
        
        # Apply cooldown (60s default)
        if not self.should_send_alert(alert_id, cooldown_seconds=60):
            print(f"⏸️  Alert suppressed (cooldown): {alert_id}")
            return
        
        # Determine severity
        severity = self._calculate_severity(violation)
        
        # Build alert message
        alert = {
            "type": "violation_alert",
            "severity": severity,
            "data": violation,
            "timestamp": datetime.now().isoformat(),
            "alert_id": alert_id
        }
        
        # Broadcast to all connected clients
        await self.broadcast(alert)
        print(f"🚨 Alert sent: {severity} - {alert_id}")
    
    def _calculate_severity(self, violation: dict) -> str:
        """Calculate severity based on violation type"""
        violation_type = violation.get('violation', '').lower()
        
        # High severity
        if 'helmet' in violation_type or 'no helmet' in violation_type:
            return 'high'
        
        # Medium severity
        if 'vest' in violation_type or 'goggles' in violation_type:
            return 'medium'
        
        # Low severity
        return 'low'
    
    async def send_stats_update(self, stats: dict):
        """Send real-time stats update"""
        message = {
            "type": "stats_update",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    async def send_camera_status(self, camera_id: str, status: str):
        """Send camera status update"""
        message = {
            "type": "camera_status",
            "camera_id": camera_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)

# Global connection manager
manager = ConnectionManager()
