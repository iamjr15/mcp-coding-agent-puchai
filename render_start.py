#!/usr/bin/env python3
"""Render.com startup script for MCP Code Generator.

This script starts the FastAPI application for deployment on Render.com
as a persistent web service rather than a serverless function.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import mcp_generator

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8086))
    
    # Run the MCP server directly (same as your astro MCP setup)
    async def run_mcp_server():
        print("\n" + "=" * 60)
        print("MCP CODE GENERATOR SERVER")
        print("=" * 60)
        print(f"[OK] Running on port: {port}")
        print(f"[OK] Environment: {'Render' if 'RENDER' in os.environ else 'Local'}")
        print("=" * 60)
        
        # Import the already-configured MCP server (it's initialized globally)
        from mcp_generator import mcp, download_manager
        from datetime import datetime
        
        # Create downloads directory
        downloads_dir = Path("static/downloads")
        downloads_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Downloads: {downloads_dir.absolute()}")
        
        # Add the custom routes that are normally added in main()
        @mcp.custom_route(methods=["GET"], path="/download/{download_id}")
        async def download_mcp_endpoint(request):
            # Extract download_id from the URL path
            path_parts = request.url.path.split('/')
            download_id = path_parts[-1]  # Get the last part of the path
            return await download_manager.serve_download(download_id)
        
        @mcp.custom_route(methods=["GET"], path="/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "MCP Code Generator",
                "timestamp": datetime.now().isoformat()
            }
        
        @mcp.custom_route(methods=["GET"], path="/download-stats")
        async def download_stats():
            from utils.zip_creator import get_download_stats
            return get_download_stats()
        
        print("=" * 60)
        print(f"Downloads: {os.environ.get('DOWNLOAD_BASE_URL', 'Not Set')}/download/")
        print("=" * 60)
        
        # Start the server with Render's port
        await mcp.run_async("streamable-http", host="0.0.0.0", port=port)
    
    # Run the MCP server directly like in your astro setup
    asyncio.run(run_mcp_server())
