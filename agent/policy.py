"""BƯỚC 3b — PEP (Policy Enforcement Point) tại tool call (15').

Cổng chặn TRƯỚC KHI tool thật sự execute. Đọc CHECKPOINTS.md (§3b).

Interface bắt buộc (tests/test_policy.py và agent/runner.py gọi trực tiếp):

    check(context: PolicyContext) -> tuple[bool, str]
        Trả về (allow, reason).
        `reason` KHÔNG BAO GIỜ được để trống — cả khi allow=True và
        allow=False. Đây là evidence audit ở Bước 4 (rubric: "Audit
        completeness = 100%" — điều kiện trượt nếu có dòng thiếu reason).

PolicyContext — 5 input gốc và các input OBO cho lớp L3:

    data_classification: str   "public" | "internal" | "restricted"
    request_purpose: str       tự do, ví dụ "reconciliation", "support-reply"
    agent_owner: str            định danh agent/run gọi tool này
    delegation_depth: int       0 = gọi trực tiếp bởi user, >0 = agent gọi agent
    egress_enabled: bool        run hiện tại có được phép gọi network không
    principal_id: str           ID người ra lệnh từ data/principals.json
    requested_tool: str         tool sắp gọi
    agent_scopes: tuple[str]    quyền tối đa của agent
    parent_scopes: tuple[str]   quyền của agent cha khi delegation_depth > 0
    expires_at: str             ISO-8601 UTC; hết hạn phải deny

Rule TỐI THIỂU bắt buộc (không được viết yếu hơn rule này):

    classification == "restricted" and egress_enabled is True  ->  DENY

Checkpoint OBO: quyền hiệu lực = principal.allowed_tools ∩ agent_scopes,
và nếu depth > 0 thì còn giao với parent_scopes. Unknown principal, scope
thiếu, run hết hạn đều deny kèm reason. Principal là fixture mô phỏng,
không phải xác thực người dùng production.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PRINCIPALS_PATH = BASE_DIR / "data" / "principals.json"
@dataclass(frozen=True)
class PolicyContext:
    data_classification: str
    request_purpose: str
    agent_owner: str
    delegation_depth: int
    egress_enabled: bool
    principal_id: str = ""
    requested_tool: str = ""
    agent_scopes: tuple[str, ...] = ()
    parent_scopes: tuple[str, ...] = ()
    expires_at: str = ""
def _load_principals() -> dict:
    if PRINCIPALS_PATH.exists():
        return json.loads(PRINCIPALS_PATH.read_text(encoding="utf-8"))
    return {}
def check(context: PolicyContext) -> tuple[bool, str]:
    # 1. Rule tối thiểu: data restricted đi kèm egress network BẮT BUỘC bị chặn
    if context.data_classification == "restricted" and context.egress_enabled:
        return False, "Prohibited: Egress is strictly forbidden when handling restricted data."
    # 2. Kiểm tra thời hạn hiệu lực (TTL)
    if context.expires_at:
        try:
            exp = datetime.fromisoformat(context.expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return False, f"Token/session expired at {context.expires_at}."
        except Exception:
            return False, f"Invalid expiration timestamp format: {context.expires_at}."
    # 3. Kiểm tra Principal và Scope hiệu lực (OBO)
    if context.principal_id:
        principals = _load_principals()
        if context.principal_id not in principals:
            return False, f"Unknown or unauthorized principal: {context.principal_id}."
        p_info = principals[context.principal_id]
        # Kiểm tra mục đích
        if context.request_purpose and p_info.get("purposes"):
            if context.request_purpose not in p_info["purposes"]:
                return False, f"Purpose {context.request_purpose!r} not permitted for principal {context.principal_id!r}."
        # Tính tập quyền hiệu lực
        effective_allowed = set(p_info.get("allowed_tools", []))
        if context.agent_scopes:
            effective_allowed &= set(context.agent_scopes)
        if context.delegation_depth > 0:
            effective_allowed &= set(context.parent_scopes)
        # Kiểm tra tool được yêu cầu
        if context.requested_tool and context.requested_tool not in effective_allowed:
            return (
                False,
                f"Tool {context.requested_tool!r} not permitted for principal {context.principal_id!r} "
                f"with effective scopes {sorted(effective_allowed)}.",
            )
    return (
        True,
        f"Operation permitted for principal {context.principal_id or 'anonymous'} "
        f"on {context.requested_tool or 'action'}.",
    )
