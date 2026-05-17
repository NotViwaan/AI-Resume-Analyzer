from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from bson import ObjectId
from app.core.dependencies import DBDep, CurrentUser
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    CREDENTIALS_EXCEPTION,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _serialize_user(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user["full_name"],
        role=user.get("role", "recruiter"),
        company=user.get("company"),
        avatar_url=user.get("avatar_url"),
        is_active=user.get("is_active", True),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DBDep):
    # Check if email already exists
    existing = await db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_doc = {
        "email": payload.email,
        "hashed_password": get_password_hash(payload.password),
        "full_name": payload.full_name,
        "company": payload.company,
        "role": "recruiter",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await db["users"].insert_one(user_doc)
    user_id = str(result.inserted_id)

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DBDep):
    user = await db["users"].find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    user_id = str(user["_id"])
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: DBDep):
    try:
        token_data = decode_token(payload.refresh_token)
    except Exception:
        raise CREDENTIALS_EXCEPTION

    if token_data.get("type") != "refresh":
        raise CREDENTIALS_EXCEPTION

    user_id = token_data.get("sub")
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("is_active", True):
        raise CREDENTIALS_EXCEPTION

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return _serialize_user(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    updates: dict,
    current_user: CurrentUser,
    db: DBDep,
):
    allowed_fields = {"full_name", "company", "avatar_url"}
    safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    safe_updates["updated_at"] = datetime.now(timezone.utc)

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": safe_updates},
    )

    updated = await db["users"].find_one({"_id": current_user["_id"]})
    return _serialize_user(updated)
