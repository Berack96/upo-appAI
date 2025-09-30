from agno.agent import Agent


class SocialAgent(Agent):
    """
    Gli agenti devono esporre un metodo run con questa firma.

    def run(
            self,
            input: Union[str, List, Dict, Message, BaseModel, List[Message]],
            *,
            stream: Optional[bool] = None,
            stream_intermediate_steps: Optional[bool] = None,
            user_id: Optional[str] = None,
            session_id: Optional[str] = None,
            session_state: Optional[Dict[str, Any]] = None,
            audio: Optional[Sequence[Any]] = None,
            images: Optional[Sequence[Any]] = None,
            videos: Optional[Sequence[Any]] = None,
            files: Optional[Sequence[Any]] = None,
            retries: Optional[int] = None,
            knowledge_filters: Optional[Dict[str, Any]] = None,
            add_history_to_context: Optional[bool] = None,
            add_dependencies_to_context: Optional[bool] = None,
            add_session_state_to_context: Optional[bool] = None,
            dependencies: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            yield_run_response: bool = False,
            debug_mode: Optional[bool] = None,
            **kwargs: Any,
        ) -> Union[RunOutput, Iterator[Union[RunOutputEvent, RunOutput]]]:
    """
    @staticmethod
    def analyze(query: str) -> str:
        # Mock analisi social
        return "💬 Sentiment social: forte interesse retail su nuove altcoin emergenti."
