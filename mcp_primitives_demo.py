# mcp_primitives_demo.py

from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("MCP-Primitive-Demo")

# 1. TOOL (Model-Controlled): Called dynamically by the LLM when needed
@mcp.tool()
def execute_sql_query(query: str) -> str:
    """Executes a database query. Invoked autonomously by model decisions."""
    return f"Query output for: {query}"

# 2. RESOURCE (Application-Controlled): Data read programmatically by host app
@mcp.resource("config://app_settings")
def get_app_settings() -> str:
    """Read-only context attached to prompt window by application host."""
    return '{"environment": "production", "version": "1.4.2"}'

# 3. PROMPT (User-Controlled): Slash command or shortcut invoked by the user
@mcp.prompt()
def analyze_code_review(code_snippet: str) -> str:
    """Pre-defined template triggered directly by user selection."""
    return f"Please review the following code for security risks:\n\n{code_snippet}"

if __name__ == "__main__":
    mcp.run()