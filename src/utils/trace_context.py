from contextvars import ContextVar
from uuid import UUID

trace_id_var: ContextVar[UUID | None] = ContextVar("trace_id", default=None)
