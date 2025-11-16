from providers.abstract import InferenceProviderAbstractClass


class InferenceProviderClient:
    """Main client class for interacting with LLMs"""

    def __init__(self, provider: InferenceProviderAbstractClass):
        self.provider = provider

    def ask(self, model_name: str, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Send a chat request to the LLM"""
        try:
            response = self.provider.set_model(model_name).set_system_prompt(
                system_prompt).set_user_prompt(user_prompt).get_response()
            return response
        except Exception as e:
            return e
