import os
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from supabase import create_client, Client
from jose import jwt, JWTError
from dotenv import load_dotenv
import aioredis

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"
RATE_LIMIT = 20  # max requests per minute

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_redis():
    return await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

# Dependency: get user from JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Rate limit on user ID
async def rate_limiter(user_id: str = Depends(get_current_user)):
    redis = await get_redis()
    key = f"rate_limit:{user_id}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    if count > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return user_id

class LLMRequest(BaseModel):
    prompt: str
    model: str

@app.post("/api/llm")
async def llm_endpoint(
    body: LLMRequest,
    user_id: str = Depends(rate_limiter)
):
    # Dummy LLM call - replace with actual model
    await asyncio.sleep(1)
    return {"response": f"Echo: {body.prompt}", "model": body.model}

# Auth endpoints
class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/api/login")
async def login(data: AuthRequest):
    res = supabase.auth.sign_in_with_password(email=data.email, password=data.password)
    if not res.get("session"):
        raise HTTPException(status_code=400, detail="Login failed")
    user_id = res["user"]["id"]
    token = jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/signup")
async def signup(data: AuthRequest):
    res = supabase.auth.sign_up(email=data.email, password=data.password)
    if res.get("error"):
        raise HTTPException(status_code=400, detail=str(res["error"]))
    user_id = res["user"]["id"]
    token = jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
