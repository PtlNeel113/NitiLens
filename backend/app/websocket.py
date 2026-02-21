"""
WebSocket handler for real-time alerts
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json
import asyncio
import redis.asyncio as aioredis
import os

from app.auth import get_current_user
from app.models.db_models import User


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis_client = None
    
    async def connect(self, websocket: WebSocket, org_id: str):
        """Accept and register new connection"""
        await websocket.accept()
        
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        
        self.active_connections[org_id].append(websocket)
        
        # Start Redis listener if not already running
        if not self.redis_client:
            await self.start_redis_listener()
    
    def disconnect(self, websocket: WebSocket, org_id: str):
        """Remove connection"""
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
            
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)
    
    async def broadcast_to_org(self, message: str, org_id: str):
        """Broadcast message to all connections in organization"""
        if org_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.active_connections[org_id].remove(connection)
    
    async def start_redis_listener(self):
        """Listen to Redis pub/sub for alerts"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = await aioredis.from_url(redis_url)
        
        pubsub = self.redis_client.pubsub()
        
        # Subscribe to all org channels
        await pubsub.psubscribe("alerts:*")
        
        # Listen for messages
        asyncio.create_task(self._redis_listener(pubsub))
    
    async def _redis_listener(self, pubsub):
        """Background task to listen for Redis messages"""
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                channel = message["channel"].decode()
                org_id = channel.split(":")[1]
                data = message["data"].decode()
                
                await self.broadcast_to_org(data, org_id)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time alerts"""
    try:
        # Authenticate user
        # Note: In production, implement proper WebSocket authentication
        # For now, we'll accept the connection and validate token
        
        # Extract org_id from token (simplified)
        # In production, decode JWT and get user info
        org_id = "demo-org-id"  # Placeholder
        
        await manager.connect(websocket, org_id)
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                
                # Echo back for heartbeat
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": data}),
                    websocket
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket, org_id)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
