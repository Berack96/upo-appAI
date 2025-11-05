from typing import Any, Generator
import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock
from app.configs import AppConfig, ModelsConfig, APIConfig, AgentsConfigs, Strategy, AppModel, Model


@pytest.mark.configs
class TestAppConfig:

    @pytest.fixture
    def valid_config_data(self) -> dict[str, Any]:
        return {
            'port': 8080,
            'gradio_share': True,
            'logging_level': 'DEBUG',
            'strategies': [
                {'name': 'TestStrategy', 'label': 'Test', 'description': 'Test strategy'}
            ],
            'models': {
                'gemini': [{'name': 'gemini-test', 'label': 'Gemini Test'}],
                'ollama': [{'name': 'test-model', 'label': 'Test Model'}]
            },
            'api': {
                'retry_attempts': 5,
                'market_providers': ['YFinanceWrapper'],
                'news_providers': ['DuckDuckGoWrapper'],
                'social_providers': ['RedditWrapper']
            },
            'agents': {
                'strategy': 'TestStrategy',
                'team_model': 'gemini-test'
            }
        }

    @pytest.fixture
    def temp_config_file(self, valid_config_data: dict[str, Any]) -> Generator[str, None, None]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config_data, f)
            yield f.name
        os.unlink(f.name)

    def test_load_valid_config(self, temp_config_file: str):
        """Test caricamento di un file di configurazione valido"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            config = AppConfig.load(temp_config_file)
            assert config.port == 8080
            assert config.gradio_share is True
            assert config.logging_level == 'DEBUG'
            assert len(config.strategies) == 1
            assert config.strategies[0].name == 'TestStrategy'

    def test_load_nonexistent_file(self):
        """Test caricamento di un file inesistente"""
        with pytest.raises(FileNotFoundError):
            AppConfig.load("nonexistent_file.yaml")

    def test_load_invalid_yaml(self):
        """Test caricamento di un file YAML malformato"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                AppConfig.load(temp_file)
        finally:
            os.unlink(temp_file)

    def test_singleton_pattern(self, temp_config_file: str):
        """Test che AppConfig sia un singleton"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            # Reset singleton for test
            if hasattr(AppConfig, 'instance'):
                delattr(AppConfig, 'instance')

            config1 = AppConfig.load(temp_config_file)
            config2 = AppConfig.load(temp_config_file)
            assert config1 is config2

    def test_get_model_by_name_success(self, valid_config_data: dict[str, Any]):
        """Test recupero modello esistente"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            config = AppConfig(**valid_config_data)
            model = config.get_model_by_name('gemini-test')
            assert model.name == 'gemini-test'
            assert model.label == 'Gemini Test'

    def test_get_model_by_name_not_found(self, valid_config_data: dict[str, Any]):
        """Test recupero modello inesistente"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            config = AppConfig(**valid_config_data)
            with pytest.raises(ValueError, match="Model with name 'nonexistent' not found"):
                config.get_model_by_name('nonexistent')

    def test_get_strategy_by_name_success(self, valid_config_data: dict[str, Any]):
        """Test recupero strategia esistente"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            config = AppConfig(**valid_config_data)
            strategy = config.get_strategy_by_name('TestStrategy')
            assert strategy.name == 'TestStrategy'
            assert strategy.label == 'Test'

    def test_get_strategy_by_name_not_found(self, valid_config_data: dict[str, Any]):
        """Test recupero strategia inesistente"""
        with patch.object(APIConfig, 'validate_providers'), \
             patch.object(ModelsConfig, 'validate_models'), \
             patch.object(AgentsConfigs, 'validate_defaults'):

            config = AppConfig(**valid_config_data)
            with pytest.raises(ValueError, match="Strategy with name 'nonexistent' not found"):
                config.get_strategy_by_name('nonexistent')


@pytest.mark.configs
class TestModelsConfig:

    def test_all_models_property(self):
        """Test proprietà all_models che combina tutti i modelli"""
        config = ModelsConfig(
            gemini=[AppModel(name='gemini-1', label='G1')],
            ollama=[AppModel(name='ollama-1', label='O1')],
            gpt=[AppModel(name='gpt-1', label='GPT1')]
        )

        all_models = config.all_models
        assert len(all_models) == 3
        names = [m.name for m in all_models]
        assert 'gemini-1' in names
        assert 'ollama-1' in names
        assert 'gpt-1' in names

    @patch('app.configs.os.getenv')
    def test_validate_online_models_with_api_key(self, mock_getenv: MagicMock):
        """Test validazione modelli online con API key presente"""
        mock_getenv.return_value = "test_api_key"

        config = ModelsConfig(gemini=[AppModel(name='gemini-test')])
        config.validate_models()

        assert config.gemini[0].model is not None

    @patch('app.configs.os.getenv')
    def test_validate_online_models_without_api_key(self, mock_getenv: MagicMock):
        """Test validazione modelli online senza API key"""
        mock_getenv.return_value = None

        config = ModelsConfig(gemini=[AppModel(name='gemini-test')])
        config.validate_models()

        assert len(config.gemini) == 0

    @patch('app.configs.ollama.list')
    def test_validate_ollama_models_available(self, mock_ollama_list: MagicMock):
        """Test validazione modelli Ollama disponibili"""
        mock_ollama_list.return_value = {
            'models': [{'model': 'test-model'}, {'model': 'another-model'}]
        }

        config = ModelsConfig(ollama=[
            AppModel(name='test-model'),
            AppModel(name='unavailable-model')
        ])
        config._ModelsConfig__validate_ollama_models()  # type: ignore

        assert len(config.ollama) == 1
        assert config.ollama[0].name == 'test-model'
        assert config.ollama[0].model is not None

    @patch('app.configs.ollama.list')
    def test_validate_ollama_models_server_error(self, mock_ollama_list: MagicMock):
        """Test validazione modelli Ollama con nessun modello disponibile"""
        mock_ollama_list.side_effect = Exception("Connection error")

        config = ModelsConfig(ollama=[])
        config._ModelsConfig__validate_ollama_models()  # type: ignore

        assert len(config.ollama) == 0


@pytest.mark.configs
class TestAPIConfig:

    @patch('app.configs.importlib.import_module')
    def test_validate_providers_success(self, mock_import: MagicMock):
        """Test validazione provider con provider validi"""
        mock_module = MagicMock()
        mock_module.__all__ = ['TestWrapper']
        mock_module.TestWrapper = MagicMock()
        mock_import.return_value = mock_module

        config = APIConfig(
            market_providers=['TestWrapper'],
            news_providers=['TestWrapper'],
            social_providers=['TestWrapper']
        )

        config.validate_providers()  # Should not raise

    @patch('app.configs.importlib.import_module')
    def test_validate_providers_no_valid_providers(self, mock_import: MagicMock):
        """Test validazione provider senza provider validi"""
        mock_module = MagicMock()
        mock_module.__all__ = ['ValidWrapper']
        mock_import.return_value = mock_module

        config = APIConfig(market_providers=['InvalidWrapper'])

        with pytest.raises(ValueError, match="No valid markets providers found"):
            config.validate_providers()

    @patch('app.configs.importlib.import_module')
    def test_validate_providers_with_exceptions(self, mock_import: MagicMock):
        """Test validazione provider con eccezioni durante l'inizializzazione"""
        mock_module = MagicMock()
        mock_module.__all__ = ['TestWrapper']
        mock_module.TestWrapper.side_effect = Exception("Init error")
        mock_import.return_value = mock_module

        config = APIConfig(market_providers=['TestWrapper'])

        with pytest.raises(ValueError, match="No valid markets providers found"):
            config.validate_providers()


@pytest.mark.configs
class TestAgentsConfigs:

    def test_validate_defaults_success(self):
        """Test validazione defaults con configurazioni valide"""
        mock_config = MagicMock()
        mock_config.get_strategy_by_name.return_value = Strategy(name='TestStrategy')
        mock_config.get_model_by_name.return_value = AppModel(name='test-model')

        agents_config = AgentsConfigs(
            strategy='TestStrategy',
            team_model='test-model',
            team_leader_model='test-model',
            query_analyzer_model='test-model',
            report_generation_model='test-model'
        )

        agents_config.validate_defaults(mock_config)  # Should not raise

    def test_validate_defaults_invalid_strategy(self):
        """Test validazione defaults con strategia inesistente"""
        mock_config = MagicMock()
        mock_config.get_strategy_by_name.side_effect = ValueError("Strategy not found")

        agents_config = AgentsConfigs(strategy='InvalidStrategy')

        with pytest.raises(ValueError, match="Strategy not found"):
            agents_config.validate_defaults(mock_config)

    def test_validate_defaults_invalid_model(self):
        """Test validazione defaults con modello inesistente"""
        mock_config = MagicMock()
        mock_config.get_strategy_by_name.return_value = Strategy(name='TestStrategy')
        mock_config.get_model_by_name.side_effect = ValueError("Model not found")

        agents_config = AgentsConfigs(
            strategy='TestStrategy',
            team_model='invalid-model'
        )

        with pytest.raises(ValueError, match="Model not found"):
            agents_config.validate_defaults(mock_config)


@pytest.mark.configs
class TestAppModel:

    @pytest.fixture
    def mock_model_instance(self) -> tuple[MagicMock, type[Model]]:
        mock_instance = MagicMock()

        # Use a concrete subclass of the application's Model base so pydantic validation passes,
        # and make instantiation return the mock instance.
        class DummyModel(Model):
            def __new__(cls, id: str, instructions: list[str]):
                return mock_instance
        return mock_instance, DummyModel

    def test_get_model_success(self, mock_model_instance: tuple[MagicMock, type[Model]]):
        """Test creazione modello con classe impostata"""
        app_model = AppModel(name='test-model', model=mock_model_instance[1])
        result = app_model.get_model("test instructions")
        assert result == mock_model_instance[0]

    def test_get_model_no_class_set(self):
        """Test creazione modello senza classe impostata"""
        app_model = AppModel(name='test-model')

        with pytest.raises(ValueError, match="Model class for 'test-model' is not set"):
            app_model.get_model("test instructions")

    def test_get_agent_success(self, mock_model_instance: tuple[MagicMock, type[Model]]):
        """Test creazione agente con modello valido"""
        with patch('app.configs.Agent') as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_class.return_value = mock_agent_instance

            app_model = AppModel(name='test-model', model=mock_model_instance[1])
            result = app_model.get_agent(instructions="test instructions", name="agent_name")
            mock_agent_class.assert_called_once()
            assert result == mock_agent_instance


@pytest.mark.configs
class TestStrategy:

    def test_strategy_defaults(self):
        """Test valori di default per Strategy"""
        strategy = Strategy()
        assert strategy.name == "Conservative"
        assert strategy.label == "Conservative"
        assert "low-risk" in strategy.description.lower()

    def test_strategy_custom_values(self):
        """Test Strategy con valori personalizzati"""
        strategy = Strategy(
            name="Aggressive",
            label="High Risk",
            description="High-risk strategy"
        )
        assert strategy.name == "Aggressive"
        assert strategy.label == "High Risk"
        assert strategy.description == "High-risk strategy"
