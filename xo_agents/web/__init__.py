"""
XO Agents Web Module

FastAPI webhook router and middleware for agent task dispatching.
"""

from .webhook_router import router

__all__ = ["router"]
