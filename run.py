"""서버 실행 진입점입니다.

    python run.py

브라우저에서 http://localhost:8021 로 접속하세요.
"""
import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8021")),
        reload=True,
    )
