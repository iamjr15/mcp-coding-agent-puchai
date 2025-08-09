"""
Blaxel Client for MCP Code Generator

Manages Blaxel sandbox creation and interaction for code generation.
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, Optional

from blaxel.core import SandboxInstance
from blaxel.core.authentication import CredentialsType
from blaxel.core import get_credentials
from openai import AsyncOpenAI
from dotenv import dotenv_values

logger = logging.getLogger(__name__)


class BlaxelClient:
    """Client for managing Blaxel sandboxes and code generation."""
    
    def __init__(self):
        """Initialize Blaxel client."""
        # Load environment variables from .env file (for local dev) + system env (for Render)
        env_vars = dotenv_values(".env")
        
        def get_env_var(key: str, default: str = None) -> str:
            """Get environment variable from .env file or system environment (fallback for Render)."""
            return env_vars.get(key) or os.environ.get(key, default)
        
        self.workspace = get_env_var("BL_WORKSPACE")
        self.api_key = get_env_var("BL_API_KEY")
        self.morph_api_key = get_env_var("MORPH_API_KEY")
        self.morph_model = get_env_var("MORPH_MODEL", "morph-v2")
        self.openai_api_key = get_env_var("OPENAI_API_KEY")
        
        # Blaxel credentials are optional (warn if missing but don't fail)
        if not all([self.workspace, self.api_key, self.morph_api_key]):
            logger.warning("Missing BL_WORKSPACE, BL_API_KEY, MORPH_API_KEY. Blaxel sandbox functionality is disabled.")
        
        if not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY for code generation")
        
        # Initialize OpenAI client for code generation
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        
        # Check if Blaxel can load credentials
        self.credentials = get_credentials()
        if not self.credentials:
            logger.warning("Blaxel credentials not found via get_credentials(), using environment variables")
            # Try to set up credentials manually
            self.credentials = CredentialsType(
                api_key=self.api_key,
                workspace=self.workspace
            )
    
    async def create_code_generation_sandbox(self, generation_id: str) -> SandboxInstance:
        """Create a Blaxel sandbox optimized for MCP code generation.
        
        Args:
            generation_id: Unique identifier for this generation session
            
        Returns:
            Configured Blaxel sandbox instance
        """
        sandbox_name = f"mcp-gen-{generation_id}-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"[{generation_id}] Creating Blaxel sandbox: {sandbox_name}")
        
        try:
            sandbox = await SandboxInstance.create_if_not_exists({
                "name": sandbox_name,
                "image": "blaxel/prod-base:latest",
                "memory": 512,  # 512MB is sufficient for code generation
                "ports": [{"target": 8000, "protocol": "HTTP"}],
                "envs": [
                    {"name": "MORPH_API_KEY", "value": self.morph_api_key},
                    {"name": "MORPH_MODEL", "value": self.morph_model},
                    {"name": "GENERATION_ID", "value": generation_id}
                ]
            })
            
            # Wait for sandbox to be ready
            await sandbox.wait()
            logger.info(f"[{generation_id}] Sandbox ready: {sandbox_name}")
            
            return sandbox
            
        except Exception as e:
            logger.error(f"[{generation_id}] Failed to create sandbox: {e}")
            raise
    
    async def cleanup_sandbox(self, sandbox: SandboxInstance, generation_id: str) -> None:
        """Clean up a Blaxel sandbox.
        
        Args:
            sandbox: Sandbox instance to clean up
            generation_id: Generation ID for logging
        """
        try:
            logger.info(f"[{generation_id}] Cleaning up sandbox: {sandbox.metadata.name}")
            await sandbox.delete(sandbox.metadata.name)
            logger.info(f"[{generation_id}] Sandbox deleted successfully")
        except Exception as e:
            logger.warning(f"[{generation_id}] Failed to cleanup sandbox: {e}")
    
    async def generate_file_content(
        self, 
        file_path: str, 
        instructions: str,
        generation_id: str
    ) -> str:
        """Generate content for a specific file using OpenAI GPT-4.
        
        Args:
            file_path: Path of file to generate
            instructions: Generation instructions
            generation_id: Generation ID for logging
            
        Returns:
            Generated file content
        """
        logger.debug(f"[{generation_id}] Generating {file_path}")
        
        try:
            # Use OpenAI GPT-4 for high-quality code generation
            logger.debug(f"[{generation_id}] Using OpenAI GPT-4 for {file_path}")
            
            # Create specialized prompts based on file type
            system_prompt = self._get_system_prompt(file_path)
            user_prompt = self._create_generation_prompt(file_path, instructions)
            
            # Generate content using GPT-4
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for best results
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent, reliable code
                max_tokens=4000   # Sufficient for most files
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up any markdown code blocks if present
            if content.startswith("```"):
                lines = content.split('\n')
                # Remove first line if it's ```language
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = '\n'.join(lines)
            
            logger.debug(f"[{generation_id}] Generated {file_path}: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"[{generation_id}] Failed to generate {file_path}: {e}")
            raise
    
    def _get_system_prompt(self, file_path: str) -> str:
        """Get specialized system prompt based on file type.
        
        Args:
            file_path: Path of the file being generated
            
        Returns:
            System prompt for the file type
        """
        if file_path == "mcp_server.py":
            return """You are an expert Python developer specializing in Model Context Protocol (MCP) servers for Puch AI.

CRITICAL: You must follow ALL Puch AI MCP requirements exactly:

1. MANDATORY imports:
   - import asyncio, os, json, uuid
   - from typing import Annotated, Optional, Literal
   - from datetime import datetime
   - from dotenv import load_dotenv
   - from fastmcp import FastMCP
   - from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
   - from mcp import ErrorData, McpError
   - from mcp.server.auth.provider import AccessToken
   - from mcp.types import TextContent, INVALID_PARAMS, INTERNAL_ERROR
   - from pydantic import BaseModel, Field

2. MANDATORY setup:
   - from dotenv import dotenv_values
   - env_vars = dotenv_values(".env")
   - AUTH_TOKEN = env_vars.get("AUTH_TOKEN")
   - MY_NUMBER = env_vars.get("MY_NUMBER")
   - assert statements for both

3. MANDATORY auth provider:
   - SimpleBearerAuthProvider class implementation
   - FastMCP initialization with auth=SimpleBearerAuthProvider(AUTH_TOKEN)

4. MANDATORY tools pattern:
   - RichToolDescription class with description, use_when, side_effects
   - validate() tool FIRST (returns MY_NUMBER)
   - All tools use @mcp.tool(description=ToolDescription.model_dump_json())
   - Include puch_user_id parameter for user-specific data
   - Proper error handling with McpError

5. MANDATORY main function:
   - async def main() with mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

Generate production-ready, complete code that implements the requested functionality while following ALL requirements."""

        elif file_path == "requirements.txt":
            return """You are generating a requirements.txt file for a Python MCP server.
Include all necessary dependencies with appropriate version constraints.
Always include fastmcp, python-dotenv, cryptography, and other MCP essentials."""

        elif file_path.endswith(".md"):
            return """You are generating professional documentation for an MCP server.
Create clear, comprehensive documentation with proper setup instructions, usage examples, and deployment guidance.
Use proper markdown formatting and include all necessary sections."""

        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return """You are generating YAML configuration files for deployment platforms like Render or Vercel.
Create proper, valid YAML with all necessary configuration for hosting MCP servers."""

        elif file_path.endswith(".py"):
            return """You are an expert Python developer creating production-ready code.
Follow Python best practices, include proper error handling, type hints, and docstrings.
Ensure code is clean, maintainable, and follows PEP 8 standards."""

        elif file_path.startswith(".env"):
            return """You are generating environment variable templates.
Include all necessary variables with clear descriptions and example values."""

        else:
            return """You are generating a configuration or project file.
Create proper, valid content following best practices for the file type."""

    def _create_generation_prompt(self, file_path: str, instructions: str) -> str:
        """Create the user prompt for file generation.
        
        Args:
            file_path: Path of the file being generated
            instructions: Generation instructions from the code generator
            
        Returns:
            User prompt for generation
        """
        return f"""Generate the complete content for the file: {file_path}

{instructions}

Requirements:
- Generate COMPLETE, production-ready content
- Follow ALL file-type specific requirements
- Include proper error handling and validation
- Do NOT include explanations or comments about the generation process
- Return ONLY the file content, ready to use

File: {file_path}"""
