import sys
import os
import uvicorn

# Add Phase 5 folder to python search path
dev_dir = os.path.join(os.path.dirname(__file__), "5.Project Development Phase")
sys.path.insert(0, dev_dir)

# Import FastAPI app from main.py inside Phase 5 folder
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # Run uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
