from pathlib import Path

__PROMPTS_PATH = Path(__file__).parent

def __load_prompt(file_name: str) -> str:
    file_path = __PROMPTS_PATH / file_name
    return file_path.read_text(encoding='utf-8').strip()

COORDINATOR_INSTRUCTIONS = __load_prompt("team_leader.txt")
MARKET_INSTRUCTIONS = __load_prompt("team_market.txt")
NEWS_INSTRUCTIONS = __load_prompt("team_news.txt")
SOCIAL_INSTRUCTIONS = __load_prompt("team_social.txt")
PREDICTOR_INSTRUCTIONS = __load_prompt("predictor.txt")

__all__ = [
    "COORDINATOR_INSTRUCTIONS",
    "MARKET_INSTRUCTIONS",
    "NEWS_INSTRUCTIONS",
    "SOCIAL_INSTRUCTIONS",
    "PREDICTOR_INSTRUCTIONS",
]