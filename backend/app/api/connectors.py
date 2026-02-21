"""
Data connector API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID
from cryptography.fernet import Fernet
import os
import base64

from app.database import get_db
from app.models.db_models import Connector, ConnectorType, ConnectorStatus
from app.auth import get_current_active_user
from app.models.db_models import User
from app.connectors import create_connector

router = APIRouter(prefix="/api/connectors", tags=["Connectors"])

# Encryption key for credentials
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())


class ConnectorCreate(BaseModel):
    connector_name: str
    connector_type: str
    connection_config: Dict[str, Any]
    field_mapping: Optional[Dict[str, str]] = None


class ConnectorResponse(BaseModel):
    connector_id: str
    connector_name: str
    connector_type: str
    status: str
    last_sync: Optional[str]
    created_at: str


@router.post("/add", response_model=ConnectorResponse)
def add_connector(
    connector_data: ConnectorCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add new data connector"""
    # Encrypt sensitive credentials
    encrypted_config = _encrypt_config(connector_data.connection_config)
    
    connector = Connector(
        org_id=current_user.org_id,
        connector_name=connector_data.connector_name,
        connector_type=ConnectorType(connector_data.connector_type),
        connection_config=encrypted_config,
        field_mapping=connector_data.field_mapping or {},
        status=ConnectorStatus.INACTIVE
    )
    
    db.add(connector)
    db.commit()
    db.refresh(connector)
    
    return {
        "connector_id": str(connector.connector_id),
        "connector_name": connector.connector_name,
        "connector_type": connector.connector_type.value,
        "status": connector.status.value,
        "last_sync": connector.last_sync.isoformat() if connector.last_sync else None,
        "created_at": connector.created_at.isoformat()
    }


@router.get("/list")
def list_connectors(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all connectors for organization"""
    connectors = db.query(Connector).filter(Connector.org_id == current_user.org_id).all()
    
    return [
        {
            "connector_id": str(c.connector_id),
            "connector_name": c.connector_name,
            "connector_type": c.connector_type.value,
            "status": c.status.value,
            "last_sync": c.last_sync.isoformat() if c.last_sync else None,
            "created_at": c.created_at.isoformat()
        }
        for c in connectors
    ]


@router.post("/test/{connector_id}")
def test_connector(
    connector_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test connector connection"""
    connector = db.query(Connector).filter(
        Connector.connector_id == connector_id,
        Connector.org_id == current_user.org_id
    ).first()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    try:
        # Decrypt config
        decrypted_config = _decrypt_config(connector.connection_config)
        
        # Create connector instance and test
        conn = create_connector(
            connector.connector_type.value,
            decrypted_config,
            connector.field_mapping
        )
        
        result = conn.test_connection()
        
        # Update status
        if result["status"] == "success":
            connector.status = ConnectorStatus.ACTIVE
        else:
            connector.status = ConnectorStatus.ERROR
        
        db.commit()
        
        return result
        
    except Exception as e:
        connector.status = ConnectorStatus.ERROR
        db.commit()
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/remove/{connector_id}")
def remove_connector(
    connector_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove connector"""
    connector = db.query(Connector).filter(
        Connector.connector_id == connector_id,
        Connector.org_id == current_user.org_id
    ).first()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    db.delete(connector)
    db.commit()
    
    return {"message": "Connector removed successfully"}


@router.get("/status/{connector_id}")
def get_connector_status(
    connector_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get connector status"""
    connector = db.query(Connector).filter(
        Connector.connector_id == connector_id,
        Connector.org_id == current_user.org_id
    ).first()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    return {
        "connector_id": str(connector.connector_id),
        "status": connector.status.value,
        "last_sync": connector.last_sync.isoformat() if connector.last_sync else None
    }


def _encrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt sensitive configuration"""
    encrypted = {}
    sensitive_keys = ["password", "api_key", "secret", "token"]
    
    for key, value in config.items():
        if any(sk in key.lower() for sk in sensitive_keys):
            encrypted[key] = cipher_suite.encrypt(str(value).encode()).decode()
        else:
            encrypted[key] = value
    
    return encrypted


def _decrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt sensitive configuration"""
    decrypted = {}
    sensitive_keys = ["password", "api_key", "secret", "token"]
    
    for key, value in config.items():
        if any(sk in key.lower() for sk in sensitive_keys):
            try:
                decrypted[key] = cipher_suite.decrypt(value.encode()).decode()
            except:
                decrypted[key] = value
        else:
            decrypted[key] = value
    
    return decrypted
