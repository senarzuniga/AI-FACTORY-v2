"""
CONTEXT LAYER - El elemento diferencial
Controla que datos ve cada agente, que cliente, que permisos.
Ningun agente accede directamente a datos - TODO pasa por esta capa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class PermissionLevel(Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_CONTROL = "full_control"
    EXTERNAL_SHARE = "external_share"


class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ADMIN_CHIEF = "admin_chief"
    CONSULTANT = "consultant"
    EXTERNAL = "external"


@dataclass
class Context:
    """Contexto completo para cada operacion."""

    client: str
    user_id: str
    user_role: UserRole
    project: Optional[str] = None

    # Fuentes de datos permitidas
    data_sources: List[str] = field(default_factory=list)

    # Permisos especificos
    permissions: Dict[str, bool] = field(default_factory=dict)

    # Metadata de la sesion
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Limite de historial
    history_limit: int = 10

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = (
                f"{self.client}_{self.user_id}_{int(datetime.now().timestamp())}"
            )

    def can_read(self, source: str) -> bool:
        """Verifica si el contexto permite leer una fuente de datos."""
        if self.user_role == UserRole.ADMIN:
            return True
        return source in self.data_sources

    def can_write(self) -> bool:
        """Verifica si el contexto permite escritura."""
        return self.permissions.get("can_write", False)

    def can_share_external(self) -> bool:
        """Verifica si puede compartir con externos."""
        return self.permissions.get("can_share_external", False)

    def to_dict(self) -> Dict:
        return {
            "client": self.client,
            "user_id": self.user_id,
            "user_role": self.user_role.value,
            "project": self.project,
            "data_sources": self.data_sources,
            "permissions": self.permissions,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
        }


class ContextManager:
    """Gestiona contextos por cliente y usuario."""

    def __init__(self) -> None:
        self.contexts: Dict[str, Context] = {}
        self.context_history: Dict[str, List[Context]] = {}

    def create_context(
        self,
        client: str,
        user_id: str,
        role: UserRole,
        project: Optional[str] = None,
    ) -> Context:
        data_sources = self._get_data_sources(client, role)
        permissions = self._get_permissions(role)

        context = Context(
            client=client,
            user_id=user_id,
            user_role=role,
            project=project,
            data_sources=data_sources,
            permissions=permissions,
        )

        key = f"{client}_{user_id}"
        self.contexts[key] = context
        self.context_history.setdefault(key, []).append(context)
        return context

    def get_context(self, client: str, user_id: str) -> Optional[Context]:
        return self.contexts.get(f"{client}_{user_id}")

    def _get_data_sources(self, client: str, role: UserRole) -> List[str]:
        base: List[str] = [
            f"sharepoint://client_{client}/01_INPUT_DATA",
            f"sharepoint://client_{client}/02_ANALYSIS",
        ]
        if role == UserRole.ADMIN:
            base += [
                "sharepoint://core/00_ADMIN",
                "sharepoint://core/02_INTERNAL_OPERATIONS",
            ]
        elif role == UserRole.MANAGER:
            base.append(f"sharepoint://client_{client}/03_PROJECTS")
        elif role == UserRole.ADMIN_CHIEF:
            base.append(f"sharepoint://client_{client}/00_GOVERNANCE")
        return base

    def _get_permissions(self, role: UserRole) -> Dict[str, bool]:
        return {
            "can_write": role in (UserRole.ADMIN, UserRole.MANAGER, UserRole.ADMIN_CHIEF),
            "can_share_external": role == UserRole.ADMIN,
            "can_delete": role == UserRole.ADMIN,
            "can_approve": role in (UserRole.ADMIN, UserRole.MANAGER),
            "can_export": role != UserRole.EXTERNAL,
        }
