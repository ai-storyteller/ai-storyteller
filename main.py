# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anywidget",
#     "docling",
#     "fastapi",
#     "google-cloud-secret-manager",
#     "google-crc32c",
#     "IPython",
#     "itsdangerous",
#     "jinja2",
#     "langchain",
#     "langchain-community",
#     "langchain-core",
#     "langchain-openai",
#     "langchain",
#     "marimo>=0.11.29",
#     "matplotlib",
#     "openai",
#     "openpyxl",
#     "passlib",
#     "protobuf",
#     "pyarrow",
#     "pydantic",
#     "pygments",
#     "python-dotenv",
#     "python-multipart",
#     "sentence-transformers",
#     "starlette",
#     "tiktoken",
#     "traitlets",
# ]
# ///

import json
import logging
import os
from contextlib import suppress
from pathlib import Path
from typing import Any

import marimo
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DEBUG = os.getenv("DEBUG", False)
DEFAULT_PORT = 8000
PORT = os.getenv("PORT", f"{DEFAULT_PORT}")
try:
    PORT = int(PORT)
except ValueError:
    PORT = DEFAULT_PORT

OPEN_DASHBOARD_APPS_IN_NEW_TAB = os.getenv("OPEN_DASHBOARD_APPS_IN_NEW_TAB", False)

# -----------------------------------------------------------------------------
# Application list configuration
# -----------------------------------------------------------------------------

ui_dir = os.path.join(os.path.dirname(__file__), "playground")
templates_dir = os.path.join(os.path.dirname(__file__), "playground", "templates")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)

server = marimo.create_asgi_app()
apps_list: list[dict[str, Any]] = []

for filename in sorted(os.listdir(ui_dir)):
    if filename.endswith(".py") and not filename.startswith("_"):
        app_name = os.path.splitext(filename)[0]
        app_path = os.path.join(ui_dir, filename)
        app_info_path = Path(ui_dir) / f"{app_name}.json"
        app_info = {
            "title": app_name,
            "description": "",
            "path": app_name,
        }
        if app_info_path.exists() and app_info_path.is_file():
            with suppress(Exception):
                _app_info = json.loads(app_info_path.read_text())
                app_info.update(_app_info)
        server = server.with_app(path=f"/{app_name}", root=app_path)
        apps_list.append(app_info)

# -----------------------------------------------------------------------------
# FastAPI init
# -----------------------------------------------------------------------------
app = FastAPI()

# -----------------------------------------------------------------------------
# API helpers
# -----------------------------------------------------------------------------
DISABLE_AUTHENTICATION = str(
    os.getenv("DISABLE_AUTHENTICATION", "")
).lower() in {"1", "true", "yes", "on"}


def get_current_user(request: Request):
    # If authentication is disabled, return a dummy user.
    if DISABLE_AUTHENTICATION:
        # return {"name": "Anonymous", "email": "anonymous@localhost"}
        return None

    user = request.session.get("user")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user


# -----------------------------------------------------------------------------
# Authentication middleware for Marimo
# -----------------------------------------------------------------------------
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add user data to the request scope
        # This will be accessible via `mo.app_meta().request.user`
        if DISABLE_AUTHENTICATION:
            request.scope["user"] = {
                "is_authenticated": False,
            }
            # request.scope["user"] = {
            #     "is_authenticated": True,
            #     "username": "Anonymous",
            #     "email": "anonymous@localhost",
            # }
        else:
            user = request.session.get("user")
            request.scope["user"] = (
                {
                    "is_authenticated": True,
                    "username": user["name"],
                    "email": user["email"],
                    # Add any other user data
                }
                if user
                else {"is_authenticated": False}
            )

        # Optional add metadata to the request
        _url_parts = request.url.path.split("/")
        request.scope["meta"] = {
            "user": request.scope["user"],  # keep user in meta; works in both modes
            "url_path": _url_parts[1] if len(_url_parts) > 1 else None,
        }

        response = await call_next(request)
        return response


# Add the middleware to FastAPI app
app.add_middleware(AuthMiddleware)

# -----------------------------------------------------------------------------
# Exception handling
# -----------------------------------------------------------------------------


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    LOGGER.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail},
        status_code=exc.status_code,
    )


# -----------------------------------------------------------------------------
# Session
# -----------------------------------------------------------------------------

# Configure session middleware for storing user info (e.g., after login)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# -----------------------------------------------------------------------------
# OAuth2 configuration
# -----------------------------------------------------------------------------

# Set your Google OAuth credentials via environment variables or replace with your values
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
ALLOWED_DOMAINS = ("gmail.com",)

# Initialize OAuth and register the Google provider
oauth = OAuth()
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)


# -----------------------------------------------------------------------------
# Home endpoint
# -----------------------------------------------------------------------------


@app.get("/")
async def home(request: Request):
    user = request.session.get("user")
    # if DISABLE_AUTHENTICATION and not user:
    #     user = {"name": "Anonymous", "email": "anonymous@localhost"}

    if user or DISABLE_AUTHENTICATION:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "apps": apps_list,
                "open_apps_in_new_tab": OPEN_DASHBOARD_APPS_IN_NEW_TAB,
            },
        )
    return templates.TemplateResponse("home.html", {"request": request})


# -----------------------------------------------------------------------------
# Ping endpoint
# -----------------------------------------------------------------------------


@app.get("/ping")
async def root():
    return {"message": "pong"}


# -----------------------------------------------------------------------------
# Login endpoint
# -----------------------------------------------------------------------------
DISABLE_HTTPS_ENFORCEMENT = os.getenv("DISABLE_HTTPS_ENFORCEMENT", False)


@app.get("/login")
async def login(request: Request):
    # The 'hd' parameter hints to Google to display only accounts from ALLOWED_DOMAIN
    if DISABLE_AUTHENTICATION:
        # request.session["user"] = {
        #     "name": "Anonymous",
        #     "email": "anonymous@example.com",
        # }
        return RedirectResponse(url="/")

    redirect_uri = request.url_for("auth")
    redirect_uri = str(redirect_uri)
    if not DISABLE_HTTPS_ENFORCEMENT and redirect_uri.startswith("http://"):
        redirect_uri = redirect_uri.replace("http://", "https://", 1)
    # return await oauth.google.authorize_redirect(request, redirect_uri, hd=ALLOWED_DOMAIN)
    return await oauth.google.authorize_redirect(request, redirect_uri)


# -----------------------------------------------------------------------------
# Auth callback endpoint
# -----------------------------------------------------------------------------


@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error.error}")
    LOGGER.info(token)
    # Try to parse the id_token if it exists, else fallback to the userinfo endpoint.
    login_success = False
    user = None
    if "id_token" in token:
        try:
            user = await oauth.google.parse_id_token(request, token)
            login_success = True
        except Exception as err:
            LOGGER.error(err)

    if not login_success:
        userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
        # Fallback: call the userinfo endpoint to get user data.
        resp = await oauth.google.get(userinfo_endpoint, token=token)
        user = resp.json()

    # Validate the email domain
    user_email = user.get("email", "")
    # if not user_email.endswith(f"@{ALLOWED_DOMAIN}"):
    if not any(user_email.endswith(f"@{domain}") for domain in ALLOWED_DOMAINS):
        raise HTTPException(status_code=403, detail="Unauthorized domain")

    request.session["user"] = dict(user)
    return RedirectResponse(url="/")


# -----------------------------------------------------------------------------
# Logout endpoint
# -----------------------------------------------------------------------------


@app.get("/logout")
async def logout(request: Request):
    user = request.session.get("user")
    request.session.clear()
    LOGGER.info(f"User {user['name']} ({user['email']}) logged out")
    return RedirectResponse(url="/")


# -----------------------------------------------------------------------------
# Media files
# -----------------------------------------------------------------------------
# Path to your media directory
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
OUTPUT_MEDIA_DIR = os.path.join(os.path.dirname(__file__), "output")

# Mount the directory to serve files under /media/
app.mount("/media/output", StaticFiles(directory=OUTPUT_MEDIA_DIR, follow_symlink=True), name="output")
app.mount("/media", StaticFiles(directory=MEDIA_DIR, follow_symlink=True), name="media")

# -----------------------------------------------------------------------------
# Mounting the app
# -----------------------------------------------------------------------------
app.mount("/", server.build())


# -----------------------------------------------------------------------------
# Run the server
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        proxy_headers=True,
        ws_ping_interval=20,
        ws_ping_timeout=20,
        reload=DEBUG,
    )
