#!/bin/bash

# 필요한 명령어가 있는지 확인하는 함수
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 컨테이너 런타임 감지 (podman 우선, 없으면 docker)
if command_exists podman; then
    CONTAINER_CMD="podman"
elif command_exists docker; then
    CONTAINER_CMD="docker"
else
    echo "Error: podman 또는 docker가 설치되어 있지 않습니다."
    exit 1
fi

# 포트 정리 함수
cleanup_port() {
    echo "Check & Clean port 8000..."
    fuser -k 8000/tcp >/dev/null 2>&1 || true
}

# DB 준비 대기 함수
wait_for_db() {
    echo "Waiting for MySQL to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); s.connect(('127.0.0.1', 3306))" 2>/dev/null; then
            echo " MySQL port is open!"
            # 연결 가능해도 내부 초기화가 덜 되었을 수 있으므로 대기
            echo "Waiting 10s for MySQL initialization..."
            sleep 10
            return 0
        fi
        printf "."
        sleep 1
        timeout=$((timeout - 1))
    done
    echo " Timeout waiting for MySQL."
    return 1
}

# DB 컨테이너 시작 함수
start_db() {
    if $CONTAINER_CMD ps | grep -q carrot-db; then
        echo "Database 'carrot-db' is already running."
    else
        if $CONTAINER_CMD ps -a | grep -q carrot-db; then
            echo "Starting existing 'carrot-db' container..."
            $CONTAINER_CMD start carrot-db
        else
            echo "Creating and starting new 'carrot-db' container..."
            $CONTAINER_CMD run --name carrot-db \
              -e MYSQL_ROOT_PASSWORD=password \
              -e MYSQL_DATABASE=carrot_db \
              -e MYSQL_USER=user \
              -e MYSQL_PASSWORD=password \
              -p 3306:3306 \
              -d mysql:8
        fi
    fi
    wait_for_db
}

# 환경 변수 설정 함수
setup_env() {
    if [ ! -f .env.local ]; then
        echo "Creating .env.local..."
        cat <<INNEREOF > .env.local
# === Database ===
DB_DIALECT=mysql
DB_DRIVER=aiomysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=user
DB_PASSWORD=password
DB_DATABASE=carrot_db

# === Auth (Dummy Values for Dev) ===
GOOGLE_CLIENT_ID=dummy_id
GOOGLE_CLIENT_SECRET=dummy_secret
FRONTEND_URL=http://localhost:5173
ACCESS_TOKEN_SECRET=dev_access_secret
REFRESH_TOKEN_SECRET=dev_refresh_secret
SESSION_SECRET=dev_session_secret
INNEREOF
    fi
}

# 마이그레이션 파일 핫픽스 (FK 오류 해결)
fix_migration() {
    TARGET_FILE="carrot/db/migrations/versions/4c9ffeff6c6a_.py"
    if [ -f "$TARGET_FILE" ]; then
        if grep -q "sa.PrimaryKeyConstraint('id', 'category_id')" "$TARGET_FILE"; then
             echo "Fixing PK constraint in $TARGET_FILE..."
             sed -i "s/sa.PrimaryKeyConstraint('id', 'category_id')/sa.PrimaryKeyConstraint('id')/" "$TARGET_FILE"
        fi
    fi
}

# 필수 의존성 확인 및 설치
check_deps() {
    echo "Checking dependencies..."
    if ! python3 -c "import aiomysql" 2>/dev/null; then
        echo "Installing aiomysql..."
        pip install aiomysql
    fi
}

# 전체 초기화 및 실행 (기존 스크립트 동작)
run_reset() {
    cleanup_port
    echo "Removing old container..."
    $CONTAINER_CMD rm -f carrot-db || true
    
    start_db
    
    # .env.local 강제 재생성 (드라이버 변경 반영을 위해)
    rm -f .env.local
    setup_env

    source venv/bin/activate
    check_deps      # aiomysql 설치 확인
    fix_migration   # 마이그레이션 파일 수정

    echo "Running migrations..."
    alembic upgrade head

    echo "Starting Server..."
    uvicorn carrot.main:app --reload
}

# 서버만 실행 (DB가 없으면 켬)
run_server() {
    cleanup_port
    start_db
    setup_env
    
    source venv/bin/activate
    check_deps      # aiomysql 설치 확인
    fix_migration   # 마이그레이션 파일 수정

    echo "Running migrations..."
    alembic upgrade head
    
    echo "Starting Server..."
    uvicorn carrot.main:app --reload
}

# 의존성 설치
install_deps() {
    if command_exists uv; then
        echo "Syncing dependencies with uv..."
        uv sync
    else
        echo "uv not found. Please install uv or use pip manually."
        source venv/bin/activate
        pip install -r requirements.txt
    fi
}

# 지역 데이터 시딩
seed_data() {
    setup_env
    source venv/bin/activate
    check_deps
    echo "Seeding regions..."
    python3 seed_regions.py
}

# 메뉴 표시
echo "====================================="
echo "       Carrot Server Menu"
echo "====================================="
echo "1. Run Server (Start DB if needed)"
echo "2. Factory Reset (Remove DB & Run)"
echo "3. Install Dependencies (uv sync)"
echo "4. Seed Regions"
echo "5. Exit"
echo "====================================="
read -p "Select an option: " choice

case $choice in
    1) run_server ;;
    2) run_reset ;;
    3) install_deps ;;
    4) seed_data ;;
    5) exit 0 ;;
    *) echo "Invalid option." ;;
esac
