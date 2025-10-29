import os
import threading
import ollama
import yaml
import logging.config
from typing import Any, ClassVar
from pydantic import BaseModel
from agno.agent import Agent
from agno.tools import Toolkit
from agno.models.base import Model
from agno.models.google import Gemini
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.models.deepseek import DeepSeek
# from agno.models.xai import xAI

log = logging.getLogger(__name__)



class AppModel(BaseModel):
    name: str = "gemini-2.0-flash"
    label: str = "Gemini"
    model: type[Model] | None = None

    def get_model(self, instructions: str) -> Model:
        """
        Restituisce un'istanza del modello specificato.
        Args:
            instructions: istruzioni da passare al modello (system prompt).
        Returns:
             Un'istanza di BaseModel o una sua sottoclasse.
        Raise:
            ValueError se il modello non è supportato.
        """
        if self.model is None:
            raise ValueError(f"Model class for '{self.name}' is not set.")
        return self.model(id=self.name, instructions=[instructions])

    def get_agent(self, instructions: str, name: str = "", output_schema: type[BaseModel] | None = None, tools: list[Toolkit] | None = None) -> Agent:
        """
        Costruisce un agente con il modello e le istruzioni specificate.
        Args:
            instructions: istruzioni da passare al modello (system prompt)
            name: nome dell'agente (opzionale)
            output: schema di output opzionale (Pydantic BaseModel)
            tools: lista opzionale di strumenti (tools) da fornire all'agente
        Returns:
             Un'istanza di Agent.
        """
        return Agent(
            model=self.get_model(instructions),
            name=name,
            retries=2,
            tools=tools,
            delay_between_retries=5, # seconds
            output_schema=output_schema
        )



class APIConfig(BaseModel):
    retry_attempts: int = 3
    retry_delay_seconds: int = 2
    market_providers: list[str] = []
    news_providers: list[str] = []
    social_providers: list[str] = []



class Strategy(BaseModel):
    name: str = "Conservative"
    label: str = "Conservative"
    description: str = "Focus on low-risk investments with steady returns."



class ModelsConfig(BaseModel):
    gemini: list[AppModel] = [AppModel()]
    gpt: list[AppModel] = []
    mistral: list[AppModel] = []
    deepseek: list[AppModel] = []
    ollama: list[AppModel] = []

    @property
    def all_models(self) -> list[AppModel]:
        return self.gemini + self.ollama + self.gpt + self.mistral + self.deepseek

    def validate_models(self) -> None:
        """
        Validate the configured models for each supported provider.
        """
        self.__validate_online_models(self.gemini, clazz=Gemini, key="GOOGLE_API_KEY")
        self.__validate_online_models(self.gpt, clazz=OpenAIChat, key="OPENAI_API_KEY")
        self.__validate_online_models(self.mistral, clazz=MistralChat, key="MISTRAL_API_KEY")
        self.__validate_online_models(self.deepseek, clazz=DeepSeek, key="DEEPSEEK_API_KEY")
        self.__validate_ollama_models()

    def __validate_online_models(self, models: list[AppModel], clazz: type[Model], key: str | None = None) -> None:
        """
        Validate models for online providers that require an API key.
        If the models list is empty, no validation is performed and the method returns immediately.
        If the API key is not set, the models list will be cleared.
        Args:
            models: list of AppModel instances to validate
            clazz: class of the model (e.g. Gemini)
            key: API key required for the provider (optional)
        """
        if not models:
            return

        if key and os.getenv(key) is None:
            log.warning(f"No {key} set in environment variables for {clazz.__name__}.")
            models.clear()
            return

        for model in models:
            model.model = clazz

    def __validate_ollama_models(self) -> None:
        """
        Validate models for the Ollama provider.
        """
        try:
            models_list = ollama.list()
            availables = {model['model'] for model in models_list['models']}
            not_availables: list[str] = []

            for model in self.ollama:
                if model.name in availables:
                    model.model = Ollama
                else:
                    not_availables.append(model.name)
            if not_availables:
                log.warning(f"Ollama models not available, but defined in configs: {not_availables}")

            self.ollama = [model for model in self.ollama if model.model]

        except Exception as e:
            log.warning(f"Ollama is not running or not reachable: {e}")



class AgentsConfigs(BaseModel):
    strategy: str = "Conservative"
    team_model: str = "gemini-2.0-flash"
    team_leader_model: str = "gemini-2.0-flash"
    query_analyzer_model: str = "gemini-2.0-flash"
    report_generation_model: str = "gemini-2.0-flash"

    def validate_defaults(self, configs: 'AppConfig') -> None:
        """
        Validate that the default models and strategy exist in the provided configurations.
        If any default is not found, a ValueError is raised.
        Args:
            configs: the AppConfig instance containing models and strategies.
        Raises:
            ValueError if any default model or strategy is not found.
        """
        try:
            configs.get_strategy_by_name(self.strategy)
        except ValueError as e:
            log.error(f"Default strategy '{self.strategy}' not found in configurations.")
            raise e

        for model_name in [self.team_model, self.team_leader_model, self.query_analyzer_model, self.report_generation_model]:
            try:
                configs.get_model_by_name(model_name)
            except ValueError as e:
                log.error(f"Default agent model '{model_name}' not found in configurations.")
                raise e

class AppConfig(BaseModel):
    port: int = 8000
    gradio_share: bool = False
    logging_level: str = "INFO"
    api: APIConfig = APIConfig()
    strategies: list[Strategy] = [Strategy()]
    models: ModelsConfig = ModelsConfig()
    agents: AgentsConfigs = AgentsConfigs()

    __lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def load(cls, file_path: str = "configs.yaml") -> 'AppConfig':
        """
        Load the application configuration from a YAML file.
        Be sure to call load_dotenv() before if you use environment variables.
        Args:
            file_path: path to the YAML configuration file.
        Returns:
            An instance of AppConfig with the loaded settings.
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        configs = cls(**data)
        log.info(f"Loaded configuration from {file_path}")
        return configs

    def __new__(cls, *args: Any, **kwargs: Any) -> 'AppConfig':
        with cls.__lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(AppConfig, cls).__new__(cls)
            return cls.instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if hasattr(self, '_initialized'):
            return

        super().__init__(*args, **kwargs)
        self.set_logging_level()
        self.models.validate_models()
        self.agents.validate_defaults(self)
        self._initialized = True

    def get_model_by_name(self, name: str) -> AppModel:
        """
        Retrieve a model configuration by its name.
        Args:
            name: the name of the model to retrieve.
        Returns:
            The AppModel instance if found.
        Raises:
            ValueError if no model with the specified name is found.
        """
        for model in self.models.all_models:
            if model.name == name:
                return model
        raise ValueError(f"Model with name '{name}' not found.")

    def get_strategy_by_name(self, name: str) -> Strategy:
        """
        Retrieve a strategy configuration by its name.
        Args:
            name: the name of the strategy to retrieve.
        Returns:
            The Strategy instance if found.
        Raises:
            ValueError if no strategy with the specified name is found.
        """
        for strat in self.strategies:
            if strat.name == name:
                return strat
        raise ValueError(f"Strategy with name '{name}' not found.")

    def set_logging_level(self) -> None:
        """
        Set the logging level based on the configuration.
        """
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False, # Keep existing loggers (e.g. third-party loggers)
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': '%(log_color)s%(levelname)s%(reset)s [%(asctime)s] (%(name)s) - %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'colored',
                    'level': self.logging_level,
                },
            },
            'root': {  # Configure the root logger
                'handlers': ['console'],
                'level': self.logging_level,
            },
            'loggers': {
                'httpx': {'level': 'WARNING'}, # Too much spam for INFO
            }
        })

        # Modify the agno loggers
        agno_logger_names = ["agno", "agno-team", "agno-workflow"]
        for logger_name in agno_logger_names:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.propagate = True
