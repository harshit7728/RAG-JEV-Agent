
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine, get_db

from app.api.routes.jev import router as jev_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.rag import router as rag_router
from app.api.routes.agent import router as agent_router

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.graph.workflow import build_graph
from app.core.logging_config import configure_logging

configure_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        settings.langgraph_checkpoint_url
    ) as checkpointer:
        # Create the checkpointer tables/migrations.
        await checkpointer.setup()

        # Compile the graph with persistent checkpoint support.
        app.state.agent_graph = build_graph(checkpointer=checkpointer)

        try:
            yield
        finally:
            await engine.dispose()



app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)



app.include_router(jev_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")

app.include_router(rag_router, prefix="/api")
app.include_router(agent_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Enterprise Agentic RAG API",
        "status": "running",
    }



@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/health/database")
async def database_health(
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("SELECT 1"))
    return {"status": "connected"}
