import os
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, MediaNotFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("instagram-bridge")

app = FastAPI(title="instagram-bridge", docs_url="/docs")

SESSION_FILE = "/data/session.json"
cl = Client()


def get_credentials():
    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    if not username or not password:
        raise RuntimeError("IG_USERNAME and IG_PASSWORD must be set")
    return username, password


def login():
    username, password = get_credentials()
    session_path = Path(SESSION_FILE)
    if session_path.exists():
        try:
            cl.load_settings(session_path)
            cl.login(username, password)
            cl.get_timeline_feed()
            logger.info("Logged in using saved session")
            return
        except LoginRequired:
            logger.warning("Saved session expired, doing fresh login")
            session_path.unlink(missing_ok=True)
    cl.login(username, password)
    cl.dump_settings(session_path)
    logger.info("Fresh login successful, session saved")


@app.on_event("startup")
async def startup():
    login()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/post/{shortcode}")
async def get_post(shortcode: str):
    try:
        media_pk = cl.media_pk_from_code(shortcode)
        media = cl.media_info(media_pk)
        result = {
            "shortcode": shortcode,
            "author": media.user.username,
            "author_full_name": media.user.full_name,
            "caption": media.caption_text,
            "timestamp": media.taken_at.isoformat() if media.taken_at else None,
            "media_type": str(media.media_type),
            "like_count": media.like_count,
            "comment_count": media.comment_count,
            "media_urls": [],
        }
        if media.resources:
            for r in media.resources:
                url = str(r.video_url or r.thumbnail_url)
                result["media_urls"].append(url)
        elif media.video_url:
            result["media_urls"].append(str(media.video_url))
        elif media.thumbnail_url:
            result["media_urls"].append(str(media.thumbnail_url))
        return result
    except MediaNotFound:
        raise HTTPException(status_code=404, detail="Post not found")
    except LoginRequired:
        login()
        raise HTTPException(status_code=503, detail="Session refreshed, retry")
    except Exception as e:
        logger.exception("Error fetching post")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{username}")
async def get_user(username: str):
    try:
        user = cl.user_info_by_username(username)
        return {
            "username": user.username,
            "full_name": user.full_name,
            "biography": user.biography,
            "follower_count": user.follower_count,
            "following_count": user.following_count,
            "media_count": user.media_count,
            "profile_pic_url": str(user.profile_pic_url_hd or user.profile_pic_url),
            "is_verified": user.is_verified,
            "is_private": user.is_private,
        }
    except Exception as e:
        logger.exception("Error fetching user")
        raise HTTPException(status_code=500, detail=str(e))
