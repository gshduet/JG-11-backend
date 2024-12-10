from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from apis.users import user_router
from apis.posts import post_router
from apis.comments import comment_router

app = FastAPI()

# 운영 환경용 CORS 설정
# origins = [
#     "*"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     allow_headers=[
#         "Content-Type",
#         "Authorization",
#         "Accept",
#         "Origin",
#         "X-Requested-With",
#     ],
#     expose_headers=["Content-Length", "Content-Range"],
#     max_age=600,  # 프리플라이트 요청 캐시 시간 (초)
# )

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def custom_openapi():
    """
    쿠키 기반 인증을 위한 OpenAPI 스키마를 커스터마이징합니다.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI Blog",
        version="1.0.0",
        description="쿠키 기반 인증이 구현된 블로그 API",
        routes=app.routes,
    )

    # 기존 security schemes를 쿠키 인증으로 변경
    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "access_token"}
    }

    # 모든 엔드포인트에 보안 정의 적용
    openapi_schema["security"] = [{"cookieAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)


@app.get("/health")
async def health_check(request: Request):
    """
    서버 상태를 확인하는 엔드포인트입니다.
    """
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    메인 페이지를 렌더링합니다.
    게시글 목록을 보여줍니다.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: int):
    """
    게시글 상세 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse("post_detail.html", {
        "request": request,
        "post_id": post_id
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """
    회원가입 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    로그인 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse("login.html", {"request": request})