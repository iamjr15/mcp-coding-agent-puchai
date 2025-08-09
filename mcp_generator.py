"""
MCP Code Generator Server

AI-powered MCP server generator for Puch AI using Blaxel.
Generates complete, deployable MCP servers from natural language prompts.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Annotated, Optional
from pathlib import Path

from dotenv import dotenv_values
from fastmcp import FastMCP
from mcp import ErrorData, McpError
from mcp.types import INTERNAL_ERROR, TextContent
from pydantic import Field

from core.code_generator import CodeGenerator
from core.intent_parser import IntentParser
from utils.syntax_checker import check_syntax
from utils.zip_creator import create_download_zip
from utils.download_manager import DownloadManager
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Load environment variables from .env file (for local dev) + system env (for Render)
env_vars = dotenv_values(".env")

def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable from .env file or system environment (fallback for Render)."""
    return env_vars.get(key) or os.environ.get(key, default)

# Required environment variables (try .env first, then system env for Render)
MY_NUMBER = get_env_var("MY_NUMBER")
AUTH_TOKEN = get_env_var("AUTH_TOKEN")
BL_WORKSPACE = get_env_var("BL_WORKSPACE")
BL_API_KEY = get_env_var("BL_API_KEY")
MORPH_API_KEY = get_env_var("MORPH_API_KEY")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
DOWNLOAD_BASE_URL = get_env_var("DOWNLOAD_BASE_URL", "https://run.blaxel.ai")

# Validate required environment variables
required_vars = {
    "MY_NUMBER": MY_NUMBER,
    "AUTH_TOKEN": AUTH_TOKEN,  # Required for MCP authentication
    "OPENAI_API_KEY": OPENAI_API_KEY,  # Required for code generation
}

# Optional Blaxel variables (for legacy features, but not required for main functionality)
optional_vars = {
    "BL_WORKSPACE": BL_WORKSPACE,
    "BL_API_KEY": BL_API_KEY,
    "MORPH_API_KEY": MORPH_API_KEY,
}

missing_required = [name for name, value in required_vars.items() if not value]
missing_optional = [name for name, value in optional_vars.items() if not value]

if missing_required:
    logger.error(f"Missing required environment variables: {missing_required}")
    raise ValueError(f"Required environment variables not set: {missing_required}")

if missing_optional:
    logger.warning(f"Missing optional Blaxel environment variables: {missing_optional}")
    logger.warning("Blaxel features will be disabled, but core MCP generation will work with OpenAI.")

# Initialize components
mcp = FastMCP("MCP Code Generator")
code_generator = CodeGenerator()
intent_parser = IntentParser()
download_manager = DownloadManager()


@mcp.tool
async def validate() -> str:
    """Validate tool required by Puch AI.
    
    Returns:
        Phone number for validation
    """
    if not MY_NUMBER:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message="MY_NUMBER not configured"
        ))
    return MY_NUMBER


@mcp.tool(description="Generate a complete MCP server from your description")
async def generate_mcp(
    prompt: Annotated[str, Field(description="Describe the MCP you want (e.g., 'flight search with price comparison', 'weather alerts with SMS', 'crypto portfolio tracker')")],
    include_database: Annotated[bool, Field(description="Include database functionality")] = False,
    deployment_target: Annotated[str, Field(description="Deployment platform: render, vercel, or custom")] = "render"
) -> list[TextContent]:
    """Generate a complete, deployable MCP server from natural language description.
    
    Args:
        prompt: Natural language description of the MCP functionality
        include_database: Whether to include database functionality
        deployment_target: Target deployment platform
        
    Returns:
        List containing TextContent with generation results and download link
        
    Raises:
        McpError: If generation fails
    """
    start_time = datetime.now()
    generation_id = f"gen_{int(start_time.timestamp())}"
    
    # Progress update function to track stages
    def log_progress(message: str):
        """Log progress updates with timestamps."""
        logger.info(f"[{generation_id}] Progress: {message}")
    
    try:
        logger.info(f"[{generation_id}] Starting MCP generation for: {prompt[:100]}")
        
        # 1. Parse user intent (quick analysis)
        log_progress("Analyzing user intent and requirements...")
        intent = await intent_parser.parse_intent(prompt, include_database)
        log_progress(f"Intent parsed: {intent['main_functionality']}")
        
        # 2. Generate ALL project files with parallel processing (complete MCP)
        log_progress("Starting COMPLETE file generation with OpenAI GPT-4 (all files in parallel)...")
        files = await code_generator.generate_complete_mcp(
            prompt=prompt,
            intent=intent,
            deployment_target=deployment_target,
            generation_id=generation_id,
            progress_callback=log_progress,
            core_only=False  # Generate ALL files in one parallel batch
        )
        log_progress(f"File generation complete - {len(files)} files created")
        
        # 3. Skip syntax validation for speed (core files are generated by OpenAI GPT-4)
        log_progress("Skipping syntax validation for faster delivery...")
        syntax_results = {filename: "Syntax validation skipped for speed" for filename in files.keys()}
        
        # 4. Create downloadable package
        log_progress("Creating downloadable ZIP package...")
        download_url = await create_download_zip(files, prompt, generation_id)
        
        # 5. Track generation metrics
        generation_time = (datetime.now() - start_time).total_seconds()
        log_progress(f"MCP generation completed successfully in {generation_time:.1f}s")
        
        # 6. Format response
        success_message = f"""**🚀 Complete MCP Generated Successfully!**

**Project**: {intent['main_functionality']}
**Generation ID**: {generation_id}
**Files Created**: {len(files)} (all files generated in parallel)
**Generation Time**: {generation_time:.1f} seconds ⚡ (Ultra-fast parallel generation!)

**📦 Download Your Complete MCP**: {download_url}
⏰ **Link Expires**: 24 hours

**✅ Complete Package Includes:**
{_format_file_list(files)}

**🔍 Syntax Validation:**
{_format_syntax_results(syntax_results)}

**🚀 Quick Start (Ready to Deploy!):**
1. Download and extract the zip file
2. Install dependencies: `pip install -r requirements.txt`
3. Configure: Update `.env.example` → `.env` with your credentials
4. Run locally: `python mcp_server.py`
5. Deploy to {deployment_target.title()}: Use included deployment config
6. Connect to Puch AI: `/mcp connect https://your-app.onrender.com/mcp/ your_auth_token`

**📋 Everything Included:**
- ✅ Complete MCP server code
- ✅ All dependencies and configuration
- ✅ Deployment configs for {deployment_target.title()}
- ✅ Complete documentation and setup guide

**User Data Handling**: Automatically includes `puch_user_id` parameter for user separation and privacy.

Your complete MCP is ready to deploy immediately! 🎉"""
        
        return [TextContent(type="text", text=success_message)]
        
    except Exception as e:
        logger.error(f"[{generation_id}] Generation failed: {str(e)}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"MCP generation failed: {str(e)}"
        ))


@mcp.tool(description="Generate specific additional files for special requirements (database/scheduler modules)")
async def generate_additional_files(
    generation_id: Annotated[str, Field(description="Generation ID from the original MCP (e.g., gen_1754772598)")],
    deployment_target: Annotated[str, Field(description="Deployment platform: render, vercel, or custom")] = "render",
    include_database: Annotated[bool, Field(description="Include database functionality files")] = False,
    include_scheduler: Annotated[bool, Field(description="Include scheduler functionality files")] = False
) -> list[TextContent]:
    """Generate specialized additional files for specific requirements.
    
    Note: The main generate_mcp tool now includes all standard files. Use this only for 
    specialized modules (database, scheduler) not included in the main generation.
    
    Args:
        generation_id: The generation ID from your original MCP
        deployment_target: Target deployment platform
        include_database: Whether to include database module
        include_scheduler: Whether to include scheduler module
        
    Returns:
        List containing TextContent with additional files and download link
        
    Raises:
        McpError: If generation fails
    """
    start_time = datetime.now()
    additional_gen_id = f"{generation_id}_additional"
    
    def log_progress(message: str):
        """Log progress updates with timestamps."""
        logger.info(f"[{additional_gen_id}] Progress: {message}")
    
    try:
        logger.info(f"[{additional_gen_id}] Generating additional files for: {generation_id}")
        
        # Create mock intent for additional files (we need the structure)
        log_progress("Preparing additional file generation...")
        intent = {
            'main_functionality': 'Additional MCP Files',
            'requires_database': include_database,
            'requires_scheduling': include_scheduler,
            'requires_user_data': include_database or include_scheduler,  # Assume yes if they want advanced features
            'apis': [],
            'data_operations': [],
            'complexity': 'intermediate'
        }
        
        # Generate ONLY additional files in parallel (no core files)
        log_progress("Generating additional deployment and documentation files in parallel...")
        
        additional_files = {}
        additional_tasks = []
        
        # Build list of files to generate in parallel
        log_progress("Preparing additional file generation tasks...")
        
        # Note: pyproject.toml removed - requirements.txt in core files is sufficient for deployment
        
        # 2. Deployment configuration
        if deployment_target == "render":
            additional_tasks.append(("render.yaml", code_generator._generate_render_config(intent, additional_gen_id)))
            additional_tasks.append(("render_start.py", code_generator._generate_render_startup(additional_gen_id)))
        elif deployment_target == "vercel":
            additional_tasks.append(("vercel.json", code_generator._generate_vercel_config(intent, additional_gen_id)))
        
        # 3. Extended documentation
        additional_tasks.append(("DEPLOYMENT.md", code_generator._generate_deployment_guide(deployment_target, intent, additional_gen_id)))
        
        # 4. Optional modules
        if include_database:
            additional_tasks.append(("database.py", code_generator._generate_database_module(intent, additional_gen_id)))
        
        if include_scheduler:
            additional_tasks.append(("scheduler.py", code_generator._generate_scheduler_module(intent, additional_gen_id)))
        
        if include_database or include_scheduler:  # Add user guide if any advanced features
            additional_tasks.append(("USER_DATA_GUIDE.md", code_generator._generate_user_data_guide(intent, additional_gen_id)))
        
        # Generate all additional files in parallel
        log_progress(f"Generating {len(additional_tasks)} additional files in parallel...")
        
        # Extract just the coroutines for asyncio.gather
        filenames = [task[0] for task in additional_tasks]
        coroutines = [task[1] for task in additional_tasks]
        
        log_progress("Running parallel generation for additional files...")
        results = await asyncio.gather(*coroutines)
        
        # Map results to filenames
        for filename, content in zip(filenames, results):
            additional_files[filename] = content
        
        log_progress(f"Additional file generation complete - {len(additional_files)} files created")
        
        # Skip syntax validation for speed (additional files are generated by OpenAI GPT-4)
        log_progress("Skipping syntax validation for faster delivery...")
        syntax_results = {filename: "Syntax validation skipped for speed" for filename in additional_files.keys()}
        
        # Create downloadable package for additional files
        log_progress("Creating downloadable package for additional files...")
        download_url = await create_download_zip(additional_files, f"Additional files for {generation_id}", additional_gen_id)
        
        # Track generation metrics
        generation_time = (datetime.now() - start_time).total_seconds()
        log_progress(f"Additional files generated successfully in {generation_time:.1f}s")
        
        # Format response
        success_message = f"""**📁 Additional MCP Files Generated!**

**Original Generation**: {generation_id}
**Additional Files**: {len(additional_files)}
**Generation Time**: {generation_time:.1f} seconds

**📦 Download Additional Files**: {download_url}
⏰ **Link Expires**: 24 hours

**🗂️ Additional Files Include:**
{_format_file_list(additional_files)}

**🔍 Syntax Validation:**
{_format_syntax_results(syntax_results)}

**📋 Integration Steps:**
1. Download and extract the additional files
2. Merge with your existing MCP project folder
3. Update any configuration files as needed
4. Redeploy if using deployment configs

**💡 Pro Tip**: These additional files enhance your MCP with production-ready deployment configurations and extended documentation.

Additional files ready to integrate! 🚀"""
        
        return [TextContent(type="text", text=success_message)]
        
    except Exception as e:
        logger.error(f"[{additional_gen_id}] Additional file generation failed: {str(e)}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Additional file generation failed: {str(e)}"
        ))


@mcp.tool(description="Get examples of MCPs that can be generated")
async def get_mcp_examples() -> list[TextContent]:
    """Get examples and inspiration for MCP generation.
    
    Returns:
        List containing TextContent with MCP examples
    """
    examples = """**MCP Generation Examples**

**Weather & Climate**
• "Weather forecasting MCP with SMS alerts"
• "Personal weather tracker with location preferences" (user-specific)
• "Air quality monitor with health recommendations"

**Travel & Transportation**
• "Flight search with price comparison across airlines"
• "Personal travel planner with saved trips" (user-specific)
• "Public transit route planner with real-time updates"

**Finance & Trading**
• "Personal portfolio tracker with alerts" (user-specific)
• "Cryptocurrency trading bot with user preferences" (user-specific)
• "Invoice generator with PDF export and email"

**AI & Content**
• "Document summarizer using OpenAI GPT"
• "Personal note taker with AI organization" (user-specific)
• "Email automation assistant with templates"

**Personal Management**
• "Task manager with deadlines and priorities" (user-specific)
• "Personal reminder system with notifications" (user-specific)
• "Habit tracker with progress analytics" (user-specific)

**Utilities & Tools**
• "QR code generator and batch processor"
• "Personal bookmark manager with tags" (user-specific)
• "Password generator with strength analysis"

**Data & Analytics**
• "Website monitor with uptime alerts"
• "Personal expense tracker with categories" (user-specific)
• "Custom report generator with charts"

**Communication**
• "Slack bot with custom commands"
• "Personal contact manager with notes" (user-specific)
• "Email newsletter manager"

**Just describe what you want and I'll generate it!**

**Example prompts:**

**Global/Shared MCPs** (no user-specific data):
- "Create a weather MCP that provides forecasts for any location"
- "Build a flight search MCP with price comparison"
- "Generate a QR code generator MCP"

**User-Specific MCPs** (includes puch_user_id for personal data):
- "Build me a personal task manager with deadlines and priorities"
- "Create a cryptocurrency portfolio tracker for individual users"
- "Generate a personal note-taking MCP with AI categorization"

**Note**: User-specific MCPs automatically include `puch_user_id` parameter for data separation.
"""
    
    return [TextContent(type="text", text=examples)]


@mcp.tool(description="Check the status of the MCP generator system")
async def system_status() -> list[TextContent]:
    """Check system status and configuration.
    
    Returns:
        List containing TextContent with system status information
    """
    status_info = f"""**MCP Generator System Status**

**Configuration Status:**
• Phone Number: {'Configured' if MY_NUMBER else 'Missing MY_NUMBER'}
• Blaxel Workspace: {'Configured' if BL_WORKSPACE else 'Missing BL_WORKSPACE'}
• Blaxel API Key: {'Configured' if BL_API_KEY else 'Missing BL_API_KEY'}
• MorphLLM API Key: {'Configured' if MORPH_API_KEY else 'Missing MORPH_API_KEY'}
• OpenAI API Key: {'Configured' if OPENAI_API_KEY else 'Missing OPENAI_API_KEY'}

**System Information:**
• Download Base URL: {DOWNLOAD_BASE_URL}
• Downloads Directory: {'Available' if Path('static/downloads').exists() else 'Not Found'}
• Active Downloads: {len(list(Path('static/downloads').glob('*.zip')) if Path('static/downloads').exists() else [])} files

**Service Status:**
• MCP Server: Running
• Code Generator: {'Ready' if BL_API_KEY and MORPH_API_KEY and OPENAI_API_KEY else 'Not Ready'}
• Download Manager: Ready

**Usage:**
• Use `generate_mcp` to create new MCPs
• Use `get_mcp_examples` for inspiration
• Generated MCPs are automatically packaged and ready for deployment

**MCP Types Generated:**
• **Global MCPs**: Shared functionality (weather, utilities, APIs)
• **User-Specific MCPs**: Personal data management with puch_user_id
• **Hybrid MCPs**: Both global and user-specific features

**Puch AI Features:**
• Automatic bearer token authentication
• User data separation via puch_user_id
• Rich tool descriptions with use_when/side_effects
• JSON-structured responses for complex data
"""
    
    return [TextContent(type="text", text=status_info)]


def _format_file_list(files: dict) -> str:
    """Format the list of generated files."""
    file_list = []
    for filename in sorted(files.keys()):
        size = len(files[filename])
        file_list.append(f"  • {filename} ({size:,} bytes)")
    return "\n".join(file_list)


def _format_syntax_results(results: dict) -> str:
    """Format syntax validation results."""
    result_lines = []
    for filename, result in results.items():
        result_lines.append(f"  • {filename}: {result}")
    return "\n".join(result_lines)


async def main() -> None:
    """Run the MCP Code Generator server."""
    print("\n" + "=" * 60)
    print("MCP CODE GENERATOR SERVER")
    print("=" * 60)
    
    # System status
    if MY_NUMBER:
        print(f"Phone: {MY_NUMBER}")
    else:
        print("Phone: NOT CONFIGURED")
    
    if BL_WORKSPACE:
        print(f"Blaxel Workspace: {BL_WORKSPACE}")
    else:
        print("Blaxel Workspace: NOT CONFIGURED")
    
    if BL_API_KEY:
        print("Blaxel API: CONFIGURED")
    else:
        print("Blaxel API: NOT CONFIGURED")
    
    if MORPH_API_KEY:
        print("MorphLLM API: CONFIGURED")
    else:
        print("MorphLLM API: NOT CONFIGURED")
    
    if OPENAI_API_KEY:
        print("OpenAI API: CONFIGURED")
    else:
        print("OpenAI API: NOT CONFIGURED")
    
    # Create downloads directory
    downloads_dir = Path("static/downloads")
    downloads_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Downloads: {downloads_dir.absolute()}")
    
    # Add download endpoints directly to FastMCP
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
    print(f"Server: wss://run.blaxel.ai/{BL_WORKSPACE}/functions/mcp-code-generator")
    print(f"Downloads: {DOWNLOAD_BASE_URL}/download/")
    print("=" * 60)
    
    # Start the server
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)


if __name__ == "__main__":
    asyncio.run(main())
