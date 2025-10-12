import os
import threading
import ollama
import yaml
import logging.config
import agno.utils.log # type: ignore
from typing import Any
from pydantic import BaseModel
from agno.agent import Agent
from agno.tools import Toolkit
from agno.models.base import Model
from agno.models.google import Gemini
from agno.models.ollama import Ollama

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
    currency: str = "USD"

class Strategy(BaseModel):
    name: str = "Conservative"
    label: str = "Conservative"
    description: str = "Focus on low-risk investments with steady returns."

class ModelsConfig(BaseModel):
    gemini: list[AppModel] = [AppModel()]
    ollama: list[AppModel] = []

    @property
    def all_models(self) -> list[AppModel]:
        return self.gemini + self.ollama

class AgentsConfigs(BaseModel):
    strategy: str = "Conservative"
    team_model: str = "gemini-2.0-flash"
    team_leader_model: str = "gemini-2.0-flash"
    predictor_model: str = "gemini-2.0-flash"

class AppConfig(BaseModel):
    port: int = 8000
    gradio_share: bool = False
    logging_level: str = "INFO"
    api: APIConfig = APIConfig()
    strategies: list[Strategy] = [Strategy()]
    models: ModelsConfig = ModelsConfig()
    agents: AgentsConfigs = AgentsConfigs()

    __lock = threading.Lock()

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
        configs.set_logging_level()
        configs.validate_models()
        log.info(f"Loaded configuration from {file_path}")
        return configs

    def __new__(cls, *args: Any, **kwargs: Any) -> 'AppConfig':
        with cls.__lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(AppConfig, cls).__new__(cls)
            return cls.instance

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

    def validate_models(self) -> None:
        """
        Validate the configured models for each provider.
        """
        self.__validate_online_models("gemini", clazz=Gemini, key="GOOGLE_API_KEY")
        self.__validate_ollama_models()

    def __validate_online_models(self, provider: str, clazz: type[Model], key: str | None = None) -> None:
        """
        Validate models for online providers like Gemini.
        Args:
            provider: name of the provider (e.g. "gemini")
            clazz: class of the model (e.g. Gemini)
            key: API key required for the provider (optional)
        """
        if getattr(self.models, provider) is None:
            log.warning(f"No models configured for provider '{provider}'.")

        models: list[AppModel] = getattr(self.models, provider)
        if key and os.getenv(key) is None:
            log.warning(f"No {key} set in environment variables for {provider}.")
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

            for model in self.models.ollama:
                if model.name in availables:
                    model.model = Ollama
                else:
                    not_availables.append(model.name)
            if not_availables:
                log.warning(f"Ollama models not available: {not_availables}")

            self.models.ollama = [model for model in self.models.ollama if model.model]

        except Exception as e:
            log.warning(f"Ollama is not running or not reachable: {e}")

