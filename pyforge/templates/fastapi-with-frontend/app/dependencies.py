"""
Shared FastAPI dependency functions (DB sessions, auth, pagination, etc.).
"""
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session

# Re-export as typed dependency alias for cleaner route signatures
SessionDep = Annotated[AsyncSession, Depends(get_session)]
