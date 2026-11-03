from mcp.server.fastmcp import FastMCP
from mcp_server.excel_tools import excel_preview, excel_summary
from mcp_server.word_tools import word_read, word_create

mcp = FastMCP("smart-office-assistant")

@mcp.tool()
def preview_excel(file_path: str) -> str:
    """Preview the first rows of an Excel workbook at a local file path."""
    return excel_preview(file_path)

@mcp.tool()
def summarize_excel(file_path: str) -> str:
    """Summarize rows, columns, missing values, and numeric statistics in an Excel workbook."""
    return excel_summary(file_path)

@mcp.tool()
def read_word(file_path: str) -> str:
    """Read paragraph text from a local DOCX document."""
    return word_read(file_path)

@mcp.tool()
def create_word(title: str, content: str, output_path: str = "output/word/mcp_created.docx") -> str:
    """Create a DOCX document at a local output path."""
    return word_create(title, content, output_path)

if __name__ == "__main__":
    mcp.run(transport="stdio")
