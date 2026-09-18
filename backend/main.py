import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.system        import router as system_router
from backend.routes.agent         import router as agent_router
from backend.routes.telemetry     import router as telemetry_router
from backend.routes.vision        import router as vision_router
from backend.routes.maintenance   import router as maintenance_router
from backend.routes.energy        import router as energy_router
from backend.routes.safety        import router as safety_router
from backend.routes.security      import router as security_router
from backend.routes.demo          import router as demo_router
from backend.routes.voice_context import router as voice_context_router
from backend.routes.incidents import router as incidents_router
from backend.routes.manufacturing import router as manufacturing_router
from backend.services.vision_service import shutdown as vision_shutdown

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    vision_shutdown()


app = FastAPI(
    title="J.A.R.V.I.S. AI Core",
    description="Just A Rather Very Intelligent System — Voice + Agentic Intelligence",
    version="10.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(agent_router)
app.include_router(voice_context_router)
app.include_router(telemetry_router)
app.include_router(vision_router)
app.include_router(maintenance_router)
app.include_router(energy_router)
app.include_router(safety_router)
app.include_router(security_router)
app.include_router(demo_router)
app.include_router(incidents_router)
app.include_router(manufacturing_router)