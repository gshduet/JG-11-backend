# 플랫폼을 명시적으로 지정하여 크로스 플랫폼 빌드 지원
FROM --platform=$TARGETPLATFORM python:3.12.1-slim

# BuildKit 사용을 위한 ARG 설정
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# 프로젝트 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# .env 파일과 프로젝트 파일들을 복사
COPY . .

# 포트 설정
EXPOSE 80

# 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]