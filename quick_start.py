"""
Quick start script for Velos - bypasses heavy dependencies for fast preview
"""
import os
os.environ["SKIP_VECTOR_STORE"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["POSTHOG_DISABLED"] = "True"

# Now import and run server
from server import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Velos Quick Preview...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
