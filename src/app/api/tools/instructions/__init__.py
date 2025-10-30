from pathlib import Path

__INSTRUCTIONS_PATH = Path(__file__).parent

def __load_tool_instruction(file_name: str) -> str:
    file_path = __INSTRUCTIONS_PATH / file_name
    return file_path.read_text(encoding='utf-8').strip()

MARKET_TOOL_INSTRUCTIONS = __load_tool_instruction("market_instructions.md")
NEWS_TOOL_INSTRUCTIONS = __load_tool_instruction("news_instructions.md")
SOCIAL_TOOL_INSTRUCTIONS = __load_tool_instruction("social_instructions.md")
PLAN_MEMORY_TOOL_INSTRUCTIONS = __load_tool_instruction("plan_memory_instructions.md")
SYMBOLS_TOOL_INSTRUCTIONS = __load_tool_instruction("symbols_instructions.md")

__all__ = [
    "MARKET_TOOL_INSTRUCTIONS",
    "NEWS_TOOL_INSTRUCTIONS",
    "SOCIAL_TOOL_INSTRUCTIONS",
    "PLAN_MEMORY_TOOL_INSTRUCTIONS",
    "SYMBOLS_TOOL_INSTRUCTIONS",
]