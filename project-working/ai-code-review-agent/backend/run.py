"""Run the FastAPI app programmatically to avoid uvicorn import/module issues
when using the CLI with reloader in this workspace.
"""
import os

if __name__ == "__main__":
    import uvicorn
    # Import the FastAPI app from main
    from main import app

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
