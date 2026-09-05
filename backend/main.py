# main.py
import logging
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

import crud
import models
import schemas
from auth import ALGORITHM, SECRET_KEY, authenticate_officer, create_access_token, get_current_officer, require_clearance
from database import connect_to_mongo, close_mongo_connection, get_officers_collection, get_threats_collection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown"""
    try:
        await connect_to_mongo()
        logger.info("MongoDB connection verified successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Intelligence Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



async def get_officers_dep() -> object:
    """Get officers collection"""
    return get_officers_collection()


async def get_threats_dep() -> object:
    """Get threats collection"""
    return get_threats_collection()


@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    officers_collection=Depends(get_officers_dep),
) -> schemas.Token:
    officer = await authenticate_officer(officers_collection, form_data.username, form_data.password)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(subject=officer.email, clearance_level=officer.clearance_level)
    return schemas.Token(access_token=token, expires_in=expires_in)


@app.post(
    "/officers",
    response_model=schemas.OfficerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_officer(
    officer_in: schemas.OfficerCreate,
    officers_collection=Depends(get_officers_dep),
    _: models.Officer = Depends(require_clearance(10)),
) -> schemas.OfficerRead:
    existing = await crud.get_officer_by_email(officers_collection, officer_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Officer with this email already exists",
        )
    return await crud.create_officer(officers_collection, officer_in)


@app.get("/officers/me", response_model=schemas.OfficerRead)
async def read_current_officer(
    current_officer: models.Officer = Depends(get_current_officer),
) -> schemas.OfficerRead:
    return current_officer


@app.post(
    "/threats",
    response_model=schemas.ThreatPostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_threat(
    post_in: schemas.ThreatPostCreate,
    threats_collection=Depends(get_threats_dep),
    _: models.Officer = Depends(lambda: get_current_officer(get_officers_dep)),
) -> schemas.ThreatPostRead:
    return await crud.create_threat_post(threats_collection, post_in)


@app.get("/threats", response_model=schemas.ThreatPostList)
async def list_threats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    min_threat_level: int | None = Query(None, ge=1, le=5),
    is_resolved: bool | None = Query(None),
    threats_collection=Depends(get_threats_dep),
    _: models.Officer = Depends(lambda: get_current_officer(get_officers_dep)),
) -> schemas.ThreatPostList:
    items, total = await crud.list_threat_posts(threats_collection, skip=skip, limit=limit, min_threat_level=min_threat_level, is_resolved=is_resolved)
    return schemas.ThreatPostList(total=total, items=items)


@app.get("/threats/{post_id}", response_model=schemas.ThreatPostRead)
async def get_threat(
    post_id: str,
    threats_collection=Depends(get_threats_dep),
    _: models.Officer = Depends(lambda: get_current_officer(get_officers_dep)),
) -> schemas.ThreatPostRead:
    post = await crud.get_threat_post(threats_collection, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat post not found")
    return post


@app.patch("/threats/{post_id}", response_model=schemas.ThreatPostRead)
async def update_threat(
    post_id: str,
    post_in: schemas.ThreatPostUpdate,
    threats_collection=Depends(get_threats_dep),
    _: models.Officer = Depends(lambda: require_clearance(3)(get_officers_dep)),
) -> schemas.ThreatPostRead:
    post = await crud.update_threat_post(threats_collection, post_id, post_in)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat post not found")
    return post


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

class ConnectionManager:
    """Tracks live WebSocket clients and fans out messages to all of them."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, officer_id: str) -> None:
        await websocket.accept()
        self._connections.setdefault(officer_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, officer_id: str) -> None:
        sockets = self._connections.get(officer_id)
        if sockets and websocket in sockets:
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(officer_id, None)

    async def broadcast(self, message: str) -> None:
        dead: list[tuple[str, WebSocket]] = []
        for officer_id, sockets in self._connections.items():
            for ws in sockets:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append((officer_id, ws))
        for officer_id, ws in dead:
            self.disconnect(ws, officer_id)

manager = ConnectionManager()

async def _authenticate_websocket(
    websocket: WebSocket, officers_collection
) -> models.Officer | None:
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    officer = await crud.get_officer_by_email(officers_collection, email)
    if officer is None or not officer.is_active:
        return None
    return officer

@app.websocket("/ws/live-feed")
async def live_feed(
    websocket: WebSocket,
    officers_collection=Depends(get_officers_dep),
):
    officer = await _authenticate_websocket(websocket, officers_collection)
    if officer is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    officer_id_str = str(officer.id) if officer.id else "unknown"
    await manager.connect(websocket, officer_id_str)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, officer_id_str)
    except Exception:
        manager.disconnect(websocket, officer_id_str)