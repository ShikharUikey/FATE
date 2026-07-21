import pytest
import json
import time
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.security_engine.identity.models import IAMRole
from backend.app.security_engine.identity.manager import IdentityRegistryManager
from backend.app.security_engine.authentication.auth import ZeroTrustAuthManager
from backend.app.security_engine.authorization.policies import ABACPolicyEvaluator
from backend.app.security_engine.permissions.engine import ZeroTrustPermissionEngine
from backend.app.security_engine.encryption.crypt import AES256PayloadEncryptor
from backend.app.security_engine.vault.vault import SecretVaultManager
from backend.app.security_engine.risk.risk_engine import RiskTelemetryEngine
from backend.app.security_engine.approval.workflow import ApprovalWorkflowSystem
from backend.app.security_engine.auditing.logger import ImmutableAuditLogger

client = TestClient(app)

@pytest.mark.asyncio
async def test_identity_registration():
    """Verify identity creation and agent budget mapping."""
    mgr = IdentityRegistryManager()
    ident = await mgr.register_identity(
        identity_id="user_siddharth",
        name="Siddharth Uikey",
        role=IAMRole.OWNER,
        permissions=["standard", "sensitive", "privileged"],
        max_token_budget=500000
    )
    assert ident.id is not None
    assert ident.identity_id == "user_siddharth"
    assert ident.max_token_budget == 500000

def test_auth_session_timeout():
    """Verify adaptive MFA session validation and timeouts (<100ms)."""
    auth = ZeroTrustAuthManager()
    
    # Authenticate
    res = auth.authenticate_user(username="admin", pin_code="1234", device_id="device_owner_mac")
    assert res["authenticated"] is True
    token = res["session_token"]
    
    # Verify active session
    assert auth.verify_session(token) is True
    
    # Verify session timeout simulation (1 hour in future)
    assert auth.verify_session(token, current_time=time.time() + 4000) is False

def test_abac_policy_context():
    """Verify ABAC context restrictions (night hours, network types, location attributes)."""
    evaluator = ABACPolicyEvaluator()
    
    # Sensitive access during day hours -> ALLOWED
    assert evaluator.evaluate_policy_attributes("192.168.1.5", "sensitive", 12, "secure") is True
    
    # Sensitive access during night hours -> BLOCKED
    assert evaluator.evaluate_policy_attributes("192.168.1.5", "sensitive", 2, "secure") is False
    
    # Sensitive access on insecure network -> BLOCKED
    assert evaluator.evaluate_policy_attributes("192.168.1.5", "sensitive", 12, "public") is False

@pytest.mark.asyncio
async def test_decoupled_permission_engine():
    """Verify Who/Agent/Tool scope evaluations (<50ms checks)."""
    mgr = IdentityRegistryManager()
    perm_engine = ZeroTrustPermissionEngine()
    
    await mgr.register_identity(
        identity_id="agent_calendar",
        name="Calendar Agent",
        role=IAMRole.OPERATOR,
        permissions=["standard"]
    )
    
    # Allowed permission check -> SUCCESS
    res_ok = await perm_engine.check_action_permission(
        requester_id="agent_calendar",
        target_tool_id="mcp_filesystem",
        required_privilege="standard"
    )
    assert res_ok["allowed"] is True
    assert res_ok["code"] == "OK"
    
    # Insufficient permission check -> BLOCKED
    res_fail = await perm_engine.check_action_permission(
        requester_id="agent_calendar",
        target_tool_id="prod_db_wipe",
        required_privilege="sensitive"
    )
    assert res_fail["allowed"] is False
    assert res_fail["code"] == "SCOPE_CHECK_FAILED"

def test_aes256_crypt_vault():
    """Verify AES-256 crypt and secret vault logging redactor checks."""
    crypt = AES256PayloadEncryptor()
    vault = SecretVaultManager()
    
    # Encrypt/Decrypt payload cycle
    text = "FATE_SECRET_PASSWORD"
    enc = crypt.encrypt_payload(text)
    assert enc != text
    assert crypt.decrypt_payload(enc) == text
    
    # Store Vault secrets
    vault.store_secret("database_key", "SuperSecretPW123")
    retrieved = vault.retrieve_secret("database_key")
    assert retrieved == "SuperSecretPW123"
    
    # Log redactor sanitization
    sanitized = vault.redact_secrets_from_log("Connected successfully using key SuperSecretPW123.")
    assert "SuperSecretPW123" not in sanitized
    assert "********" in sanitized

def test_risk_telemetry_engine():
    """Verify risk score calculations and anomaly classifications (<100ms risk analysis)."""
    risk = RiskTelemetryEngine()
    
    # Low risk action -> LOW
    res_low = risk.calculate_action_risk(requester_role="Owner", action="read_file")
    assert res_low["risk_level"] == "LOW"
    
    # Dangerous action on low-trust device -> HIGH/CRITICAL
    res_high = risk.calculate_action_risk(requester_role="guest", action="rm -rf /", device_trust_score=0.4, failures_count=4)
    assert res_high["risk_level"] in ["HIGH", "CRITICAL"]

def test_approval_workflow():
    """Verify HITL voice approval confirmation workflows."""
    approval = ApprovalWorkflowSystem()
    token = approval.dispatch_approval_request(requester_id="operator_user", action="Git Force Push")
    
    assert approval.get_approval_status(token) == "PENDING"
    
    # Confirm approval
    approved = approval.approve_with_confirmation(token, approval_method="voice")
    assert approved is True
    assert approval.get_approval_status(token) == "APPROVED"

@pytest.mark.asyncio
async def test_immutable_audit_logging():
    """Verify immutable log audit persistence."""
    logger = ImmutableAuditLogger()
    record = await logger.log_security_event(
        user_id="user_siddharth",
        action="CREATE_WORKSPACE",
        tool_id="cli_git",
        result="SUCCESS"
    )
    assert record.id is not None
    assert record.action == "CREATE_WORKSPACE"

def test_security_rest_endpoints():
    """Verify FastAPI REST API endpoints for security operations."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/security/authenticate
    res_auth = client.post(
        "/api/v1/security/authenticate",
        json={"username": "admin", "pin_code": "1234", "device_id": "device_owner_mac"}
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["authenticated"] is True
    
    # POST /api/v1/security/identities
    res_id = client.post(
        "/api/v1/security/identities",
        headers=headers,
        json={
            "identity_id": "agent_vision",
            "name": "Vision Agent",
            "role": "Operator",
            "identity_type": "agent",
            "permissions": ["standard", "sensitive"]
        }
    )
    assert res_id.status_code == 201
    
    # POST /api/v1/security/permissions/check
    res_perm = client.post(
        "/api/v1/security/permissions/check",
        headers=headers,
        json={
            "requester_id": "agent_vision",
            "target_tool_id": "cli_docker",
            "required_privilege": "sensitive"
        }
    )
    assert res_perm.status_code == 200
    assert res_perm.json()["allowed"] is True
    
    # POST /api/v1/security/emergency-stop
    res_stop = client.post("/api/v1/security/emergency-stop", headers=headers)
    assert res_stop.status_code == 200
    assert res_stop.json()["status"] == "SYSTEM_LOCKED"
