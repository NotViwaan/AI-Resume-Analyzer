from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token, CREDENTIALS_EXCEPTION
from app.db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncIOMotorDatabase:
    return await get_database()


DBDep = Annotated[AsyncIOMotorDatabase, Depends(get_db)]


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    payload = decode_token(token)
    token_type = payload.get("type")
    if token_type != "access":
        raise CREDENTIALS_EXCEPTION
    user_id = payload.get("sub")
    if not user_id:
        raise CREDENTIALS_EXCEPTION
    return user_id


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: DBDep,
) -> dict:
    from bson import ObjectId

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentUserID = Annotated[str, Depends(get_current_user_id)]
