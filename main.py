import uvicorn
from fastapi import FastAPI
from database.database import engine, Base, async_session_maker
from routers import user_router, equipment_router, request_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.role import Role, RoleEnum
from sqlalchemy import select

async def initialize_roles():
    async with async_session_maker() as session:
        # Check if roles already exist
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if not existing_roles:
            # Create default roles
            roles = [
                Role(id=1, name=RoleEnum.admin),
                Role(id=2, name=RoleEnum.user),
                Role(id=3, name=RoleEnum.logistician)
            ]
            session.add_all(roles)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Initialize roles in a separate context
    try:
        await initialize_roles()
    except Exception as e:
        print(f"Error initializing roles: {e}")
    
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router.router, prefix="/user")
app.include_router(equipment_router.router, prefix="/equipment")
app.include_router(request_router.router, prefix="/requests")

if __name__ == "__main__":
    uvicorn.run("main:app", host = "localhost", port = 8000, reload=True, workers=1)
