from typing import List

from agno.team import Team
from agno.utils.log import log_info

from app.agents.market_agent import MarketAgent
from src.app.agents.news_agent import NewsAgent
from src.app.agents.social_agent import SocialAgent
from src.app.markets import MarketAPIs
from src.app.models import AppModels
from src.app.predictor import PredictorStyle, PredictorInput, PredictorOutput, PREDICTOR_INSTRUCTIONS


class Pipeline:
    """
    Pipeline coordinata: esegue tutti gli agenti del Team, aggrega i risultati e invoca il Predictor.
    """

    def __init__(self):
        # Inizializza gli agenti
        self.market_agent = MarketAgent()
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()

        # Crea il Team
        self.team = Team(name="CryptoAnalysisTeam", members=[self.market_agent, self.news_agent, self.social_agent])

        # Modelli disponibili e Predictor
        self.available_models = AppModels.availables()
        self.predictor_model = self.available_models[0]
        self.predictor = self.predictor_model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput) # type: ignore[arg-type]

        # Stili
        self.styles = list(PredictorStyle)
        self.style = self.styles[0]

    def choose_provider(self, index: int):
        self.predictor_model = self.available_models[index]
        self.predictor = self.predictor_model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput) # type: ignore[arg-type]

    def choose_style(self, index: int):
        self.style = self.styles[index]

    def interact(self, query: str) -> str:
        """
        Esegue il Team (Market + News + Social), aggrega i risultati e invoca il Predictor.
        """
        # Step 1: raccogli output del Team
        team_results = self.team.run(query)
        if isinstance(team_results, dict):  # alcuni Team possono restituire dict
            pieces = [str(v) for v in team_results.values()]
        elif isinstance(team_results, list):
            pieces = [str(r) for r in team_results]
        else:
            pieces = [str(team_results)]
        aggregated_text = "\n\n".join(pieces)

        # Step 2: prepara input per Predictor
        predictor_input = PredictorInput(
            data=[],  # TODO: mappare meglio i dati di mercato in ProductInfo
            style=self.style,
            sentiment=aggregated_text
        )

        # Step 3: chiama Predictor
        result = self.predictor.run(predictor_input)
        prediction: PredictorOutput = result.content

        # Step 4: formatta output finale
        portfolio_lines = "\n".join(
            [f"{item.asset} ({item.percentage}%): {item.motivation}" for item in prediction.portfolio]
        )
        output = (
            f"📊 Strategia ({self.style.value}): {prediction.strategy}\n\n"
            f"💼 Portafoglio consigliato:\n{portfolio_lines}"
        )

        return output

    def list_providers(self) -> List[str]:
        return [m.name for m in self.available_models]

    def list_styles(self) -> List[str]:
        return [s.value for s in self.styles]
