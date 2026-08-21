from fastapi import FastAPI,HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import PostCreate, PostResponce, UserRead, UserCreate, UserUpdate
from app.db import User, post, Create_db_and_tables, get_async_session 
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, fastapi_users, current_active_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan)


app.include_router(fastapi_users.get_auth_router(auth_backend), prefix = '/auth/jwt', tags = ["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix = "/auth", tags = ["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix = "/auth", tags = ["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix = "/auth", tags = ["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix = "/users", tags = ["users"])


@app.post("/upload")
async def upload_post(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):

    temp_file_path = None


    try: 
        with tempfile.NamedTemporaryFile(delete=False, suffix = os.path.splitext(file.filename)[1]) as temp_file:
             temp_file_path = temp_file.name
             shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend-upload"]
            )

        

        new_post = post(
                user_id = str(user.id),
                caption = caption,
                File_Type = "video" if file.content_type.startswith("video/") else "image",
                url = upload_result.url,
                File_Name = upload_result.name,
            
            )
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)
        return new_post

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):

    result = await session.execute(select(post).order_by(post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {str(uU.id): uU.email for uU in users}
                            
    posts_data = []
    for p in posts:
        posts_data.append({
            "id": p.id,
            "user_id":str(p.user_id),
            "caption": p.caption,
            "url": p.url,
            "file_name": p.File_Name,
            "file_type": p.File_Type,
            "created_at": p.created_at.isoformat(),
            "is_owner": str(p.user_id) == str(user.id),
            "email": user_dict.get(p.user_id, "unknown")
        })
    return { "posts": posts_data }


@app.delete("/delete/{post_id}")
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(
        select(post).where(post.id == post_id)
    )

    p = result.scalars().first()

    if not p:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if str(p.user_id) != str(user.id):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this post"
        )

    await session.delete(p)
    await session.commit()

    return {"message": "Post deleted successfully"}