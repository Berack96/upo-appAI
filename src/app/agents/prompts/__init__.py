from pathlib import Path
from datetime import datetime

__PROMPTS_PATH = Path(__file__).parent

def __load_prompt(file_name: str) -> str:
    file_path = __PROMPTS_PATH / file_name
    content = file_path.read_text(encoding='utf-8').strip()
    # Replace {{CURRENT_DATE}} placeholder with actual current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    content = content.replace("{{CURRENT_DATE}}", current_date)
    return content

TEAM_LEADER_INSTRUCTIONS = __load_prompt("team_leader.txt")
MARKET_INSTRUCTIONS = __load_prompt("team_market.txt")
NEWS_INSTRUCTIONS = __load_prompt("team_news.txt")
SOCIAL_INSTRUCTIONS = __load_prompt("team_social.txt")
QUERY_CHECK_INSTRUCTIONS = __load_prompt("query_check.txt")
REPORT_GENERATION_INSTRUCTIONS = __load_prompt("report_generation.txt")

__all__ = [
    "TEAM_LEADER_INSTRUCTIONS",
    "MARKET_INSTRUCTIONS",
    "NEWS_INSTRUCTIONS",
    "SOCIAL_INSTRUCTIONS",
    "QUERY_CHECK_INSTRUCTIONS",
    "REPORT_GENERATION_INSTRUCTIONS",
]