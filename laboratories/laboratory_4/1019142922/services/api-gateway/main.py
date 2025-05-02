"""Implement a simple Api gateway redirecting to services"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import httpx
from pydantic import BaseModel

# Secret key for JWT
SECRET_KEY = "c96b7b25c6c51519035546cdd498bc5f419edda7664ffc530c304b562881cd29"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user database
fake_users_db = {
    "student1": {
        "username": "student1",
        "hashed_password": "$2b$12$FgCv9ik3DrDC6C9B46L9.u0q.wk/5CNnP1Tn/VeK044TwgU2rv.ei",
    },
    "student2": {
        "username": "student2",
        "hashed_password": "$2b$12$FgCv9ik3DrDC6C9B46L9.u0q.wk/5CNnP1Tn/VeK044TwgU2rv.ei",
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Routes
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/search", dependencies=[Depends(get_current_user)])
async def search_tutors(subject: str):
    async with httpx.AsyncClient() as client:
        # Check cache
        cache_response = await client.get(f"http://cache:8000/get/{subject}")
        if cache_response.status_code == 200 and cache_response.json().get("value"):
            return {"cached": True, "data": cache_response.json()["value"]}

        search_response = await client.get(
            f"http://search_service:8000/search?subject={subject}"
        )
        tutors = search_response.json()

        # Cache result
        await client.post(f"http://cache:8000/set/{subject}", json={"value": tutors})

        # Return response
        return {"cached": False, "data": tutors}


@app.post("/book", dependencies=[Depends(get_current_user)])
async def book_session(student_id: Annotated[int, Body()], tutor_id: Annotated[int, Body()]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://booking_service:8000/book",
            json={"student_id": student_id, "tutor_id": tutor_id},
        )
        return response.json()
