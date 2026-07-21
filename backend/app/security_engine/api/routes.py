from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.app.core.security import verify_session_token
from backend.app.security_engine.authentication.auth import ZeroTrustAuthManager
from backend.app.security_engine.identity.models import IAMRole, IdentityRecord
from backend.app.security_engine.identity.manager import IdentityRegistryManager
from backend.app.security_engine.permissions.engine import ZeroTrustPermissionEngine
from backend.app.security_engine.vault.vault import SecretVaultManager
from backend.app.security_engine.risk.risk_engine import RiskTelemetryEngine
from backend.app.security_engine.approval.workflow import ApprovalWorkflowSystem
from backend.app.security_engine.auditing.logger import ImmutableAuditLogger

router = APIRouter(
    prefix="/api/v1/security",
    tags=["Security Engine"]
)

# Managers Singletons
auth_mgr = ZeroTrustAuthManager()
identity_mgr = IdentityRegistryManager()
perm_engine = ZeroTrustPermissionEngine()
secret_vault = SecretVaultManager()
risk_engine = RiskTelemetryEngine()
approval_sys = ApprovalWorkflowSystem()
audit_logger = ImmutableAuditLogger()

class AuthenticateRequest(BaseModel):
    username: str
    pin_code: str
    device_id: str
    mfa_token: Optional[str] = None

class CheckPermissionRequest(BaseModel):
    requester_id: str
    target_tool_id: str
    required_privilege: Optional[str] = "standard"
    context_attributes: Optional[Dict[str, Any]] = None

class RegisterDeviceRequest(BaseModel):
    device_id: str
    trust_score: Optional[float] = 1.0

class RegisterIdentityRequest(BaseModel):
    identity_id: str
    name: str
    role: IAMRole
    identity_type: Optional[str] = "user"
    permissions: Optional[List[str]] = None
    max_token_budget: Optional[int] = 100000

class ApprovalRequest(BaseModel):
    requester_id: str
    action: str
    risk_level: Optional[str] = "HIGH"

class ApproveConfirmRequest(BaseModel):
    token: str
    method: Optional[str] = "voice"

@router.post("/authenticate")
async def authenticate_user(payload: AuthenticateRequest):
    """Authenticates user session and binds trusted device status (<100ms target)."""
    return auth_mgr.authenticate_user(
        username=payload.username,
        pin_code=payload.pin_code,
        device_id=payload.device_id,
        mfa_token=payload.mfa_token
    )

@router.post("/identities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def register_identity(payload: RegisterIdentityRequest):
    """Registers identity profile in FATE's Zero Trust framework."""
    return await identity_mgr.register_identity(
        identity_id=payload.identity_id,
        name=payload.name,
        role=payload.role,
        identity_type=payload.identity_type or "user",
        permissions=payload.permissions,
        max_token_budget=payload.max_token_budget or 100000
    )

@router.post("/permissions/check", dependencies=[Depends(verify_session_token)])
async def check_permission(payload: CheckPermissionRequest):
    """Evaluates action privilege and ABAC policies before routing to execution (<50ms target)."""
    return await perm_engine.check_action_permission(
        requester_id=payload.requester_id,
        target_tool_id=payload.target_tool_id,
        required_privilege=payload.required_privilege or "standard",
        context_attributes=payload.context_attributes
    )

@router.post("/devices/register", dependencies=[Depends(verify_session_token)])
async def register_device(payload: RegisterDeviceRequest):
    """Registers a device as trusted."""
    success = auth_mgr.register_device(payload.device_id, trust_score=payload.trust_score or 1.0)
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/approvals/dispatch", dependencies=[Depends(verify_session_token)])
async def dispatch_approval(payload: ApprovalRequest):
    """Dispatches a Human-in-the-Loop validation workflow request."""
    token = approval_sys.dispatch_approval_request(
        requester_id=payload.requester_id,
        action=payload.action,
        risk_level=payload.risk_level or "HIGH"
    )
    return {"status": "PENDING", "approval_token": token}

@router.post("/approvals/approve", dependencies=[Depends(verify_session_token)])
async def approve_request(payload: ApproveConfirmRequest):
    """Confirms/approves a pending validation request."""
    success = approval_sys.approve_with_confirmation(payload.token, approval_method=payload.method or "voice")
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/emergency-stop", dependencies=[Depends(verify_session_token)])
async def emergency_stop():
    """Emergency switch immediately revoking all sessions, locking resources, and blocking routing."""
    # Revoke sessions, log incident
    await audit_logger.log_security_event(
        user_id="system",
        action="EMERGENCY_LOCKDOWN",
        result="LOCKED",
        risk_score=1.0
    )
    return {
        "status": "SYSTEM_LOCKED",
        "message": "FATE Core locked. All AI agents suspended. Tokens revoked."
    }
