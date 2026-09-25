from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from fastapi import Header, HTTPException, status


@dataclass(frozen=True)
class Identity:
    subject: str
    customer_id: str
    tenant_id: str
    scopes: frozenset[str]


class DemoTokenAuthenticator:
    """Resolve opaque demo bearer tokens to server-controlled identities.

    This deliberately small adapter demonstrates the trust boundary without
    pretending that static fixture tokens are production authentication. A
    deployed version should replace it with validated OIDC/JWT claims.
    """

    def __init__(self, identities: dict[str, Identity]):
        self._identities = identities

    @classmethod
    def from_file(cls, path: Path) -> DemoTokenAuthenticator:
        rows = json.loads(path.read_text(encoding="utf-8"))
        identities: dict[str, Identity] = {}
        for row in rows:
            token = str(row["token"])
            if token in identities:
                raise ValueError("Duplicate demo authentication token")
            identities[token] = Identity(
                subject=str(row["subject"]),
                customer_id=str(row["customer_id"]),
                tenant_id=str(row["tenant_id"]),
                scopes=frozenset(map(str, row.get("scopes", []))),
            )
        return cls(identities)

    def authenticate(self, authorization: str | None) -> Identity:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="A bearer token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        identity = self._identities.get(token)
        if identity is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if "assist:read" not in identity.scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing assist:read scope")
        return identity


def bearer_header(authorization: str | None = Header(default=None)) -> str | None:
    return authorization
