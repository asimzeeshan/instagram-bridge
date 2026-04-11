# instagram-bridge

Self-hosted Instagram content bridge. Fetches post and user data via a simple REST API, powered by [instagrapi](https://github.com/subzeroid/instagrapi).

No scraping. No headless browsers. Just a lightweight FastAPI service that talks to Instagram's private API using session-based authentication.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/post/{shortcode}` | Fetch post data (caption, author, media URLs, likes, comments) |
| `GET` | `/user/{username}` | Fetch user profile (bio, followers, media count, verified status) |
| `GET` | `/docs` | Interactive Swagger docs |

### Example: Fetch a post

```bash
curl -s http://localhost:8000/post/ABC123xyz
```

```json
{
  "shortcode": "ABC123xyz",
  "author": "natgeo",
  "author_full_name": "National Geographic",
  "caption": "A rare glimpse of...",
  "timestamp": "2026-04-10T14:30:00",
  "media_type": "1",
  "like_count": 42000,
  "comment_count": 312,
  "media_urls": ["https://..."]
}
```

### Example: Fetch a user

```bash
curl -s http://localhost:8000/user/natgeo
```

```json
{
  "username": "natgeo",
  "full_name": "National Geographic",
  "biography": "Experience the world...",
  "follower_count": 283000000,
  "following_count": 150,
  "media_count": 28000,
  "profile_pic_url": "https://...",
  "is_verified": true,
  "is_private": false
}
```

## Setup

### 1. Clone and configure

```bash
git clone https://github.com/asimzeeshan/instagram-bridge.git
cd instagram-bridge
cp .env.example .env
# Edit .env with your Instagram credentials
```

### 2. Run with Docker Compose

```bash
docker compose up -d
```

The service will be available at `http://localhost:8000`.

### With nginx-proxy (automatic SSL)

If you're running [nginx-proxy-automation](https://github.com/evertramos/nginx-proxy-automation) with Let's Encrypt, set `VIRTUAL_HOST`, `LETSENCRYPT_HOST`, and `LETSENCRYPT_EMAIL` in your `.env` file.

## How it works

- Uses `instagrapi` to authenticate with Instagram's private API
- Session is persisted to `data/session.json` so you don't re-login on every restart
- If the session expires, it automatically performs a fresh login
- Runs as a single FastAPI/Uvicorn process inside a slim Python 3.11 Docker container

## Notes

- Instagram may rate-limit or challenge logins from new IPs. Using a dedicated account is recommended.
- The `data/` directory is gitignored and volume-mounted to persist sessions across container rebuilds.
- Two-factor authentication is not supported out of the box. Use an account without 2FA enabled.

## Author

[Asim Zeeshan](https://www.linkedin.com/in/asimzeeshan/)

## License

[MIT](LICENSE)
