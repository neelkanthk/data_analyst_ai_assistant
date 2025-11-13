from abc import ABC, abstractmethod


class InferenceProviderAbstractClass(ABC):
    def __init__(self, api_key: str = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def set_model(self, model_name: str = None):
        pass

    @abstractmethod
    def set_system_prompt(self, system_prompt: str = None):
        pass

    @abstractmethod
    def set_user_prompt(self, user_prompt: str = None):
        pass

    @abstractmethod
    def get_response(self) -> str:
        pass
