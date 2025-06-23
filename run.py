#!/usr/bin/env python3
"""
Docker entry point for the Customer Care AI application.
This script serves as the main entry point for the Docker container.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=5005,  # Matches the PORT environment variable in Dockerfile
        reload=False,  # Disable auto-reload in production
        workers=4,
    )
