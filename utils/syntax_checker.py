"""
Syntax Checker for MCP Code Generator

Validates generated Python code for basic syntax correctness.
"""

import ast
from typing import Dict


def check_syntax(files: Dict[str, str]) -> Dict[str, str]:
    """Check syntax of all Python files in the generated project.
    
    Args:
        files: Dictionary mapping filenames to their content
        
    Returns:
        Dictionary mapping filenames to their validation status
    """
    results = {}
    
    for filename, content in files.items():
        if filename.endswith('.py'):
            results[filename] = _check_python_syntax(filename, content)
        elif filename in ['requirements.txt', 'pyproject.toml', 'render.yaml']:
            results[filename] = _check_config_file(filename, content)
        else:
            results[filename] = "Non-code file"
    
    return results


def _check_python_syntax(filename: str, content: str) -> str:
    """Check Python file syntax using AST parsing.
    
    Args:
        filename: Name of the Python file
        content: File content to validate
        
    Returns:
        Validation result string
    """
    try:
        # Parse the content as Python AST
        ast.parse(content)
        
        # Additional checks for MCP-specific requirements
        if filename == "mcp_server.py":
            return _check_mcp_requirements(content)
        
        return "Valid Python syntax"
        
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}"
        if e.msg:
            error_msg += f": {e.msg}"
        return f"ERROR: {error_msg}"
        
    except Exception:
        return "ERROR: Parse error"


def _check_mcp_requirements(content: str) -> str:
    """Check MCP-specific requirements in the main server file.
    
    Args:
        content: MCP server file content
        
    Returns:
        Validation result with MCP-specific checks
    """
    issues = []
    
    # Check for required imports
    required_imports = [
        ("fastmcp", "FastMCP import missing"),
        ("mcp.types", "MCP types import missing"),
    ]
    
    for import_name, error_msg in required_imports:
        if import_name not in content:
            issues.append(error_msg)
    
    # Check for required validate tool
    if "async def validate(" not in content and "@mcp.tool" in content:
        issues.append("validate() tool missing")
    
    # Check for MY_NUMBER usage
    if "MY_NUMBER" not in content and "validate" in content:
        issues.append("MY_NUMBER environment variable not used")
    
    # Check for FastMCP initialization
    if "FastMCP(" not in content:
        issues.append("FastMCP initialization missing")
    
    # Check for main function
    if "if __name__ ==" not in content and "async def main(" not in content:
        issues.append("Main execution block missing")
    
    if issues:
        return f"Valid syntax, WARNING: MCP issues: {'; '.join(issues)}"
    else:
        return "Valid Python syntax and MCP compliance"


def _check_config_file(filename: str, content: str) -> str:
    """Check configuration files for basic structure.
    
    Args:
        filename: Name of the config file
        content: File content to validate
        
    Returns:
        Validation result string
    """
    if filename == "requirements.txt":
        return _check_requirements_file(content)
    elif filename == "pyproject.toml":
        return _check_pyproject_file(content)
    elif filename == "render.yaml":
        return _check_render_config(content)
    else:
        return "Config file"


def _check_requirements_file(content: str) -> str:
    """Check requirements.txt file structure.
    
    Args:
        content: Requirements file content
        
    Returns:
        Validation result string
    """
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return "ERROR: Empty requirements file"
    
    # Check for required packages
    required_packages = ["fastmcp", "python-dotenv", "httpx"]
    missing_packages = []
    
    for package in required_packages:
        if not any(package in line for line in lines):
            missing_packages.append(package)
    
    if missing_packages:
        return f"WARNING: Missing packages: {', '.join(missing_packages)}"
    
    # Check for invalid lines
    invalid_lines = []
    for i, line in enumerate(lines, 1):
        if not (
            line.startswith('#') or  # Comment
            '==' in line or '>' in line or '<' in line or  # Version specifier
            line.replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace('.', '').isalnum()  # Package name
        ):
            invalid_lines.append(f"line {i}")
    
    if invalid_lines:
        return f"WARNING: Suspicious lines: {', '.join(invalid_lines)}"
    
    return f"Valid requirements ({len(lines)} packages)"


def _check_pyproject_file(content: str) -> str:
    """Check pyproject.toml file structure.
    
    Args:
        content: Pyproject file content
        
    Returns:
        Validation result string
    """
    required_sections = ["[project]", "[build-system]"]
    missing_sections = []
    
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        return f"WARNING: Missing sections: {', '.join(missing_sections)}"
    
    # Check for required fields
    required_fields = ["name", "version", "description"]
    missing_fields = []
    
    for field in required_fields:
        if f'{field} =' not in content:
            missing_fields.append(field)
    
    if missing_fields:
        return f"WARNING: Missing fields: {', '.join(missing_fields)}"
    
    return "Valid pyproject.toml"


def _check_render_config(content: str) -> str:
    """Check render.yaml configuration.
    
    Args:
        content: Render config content
        
    Returns:
        Validation result string
    """
    required_fields = ["services:", "type:", "env:", "buildCommand:", "startCommand:"]
    missing_fields = []
    
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        return f"WARNING: Missing fields: {', '.join(missing_fields)}"
    
    # Check for Python environment
    if "env: python" not in content:
        return "WARNING: Not configured for Python"
    
    # Check for proper start command
    if "python" not in content.lower() or "start" not in content.lower():
        return "WARNING: Start command may be incorrect"
    
    return "Valid Render configuration"
