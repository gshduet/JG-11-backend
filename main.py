from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from apis.users import user_router
from apis.posts import post_router
from apis.comments import comment_router
app = FastAPI()


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


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
