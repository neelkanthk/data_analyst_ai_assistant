from google import genai
from google.genai import types
from providers.abstract import InferenceProviderAbstractClass
from providers.providertypes import InferenceProviderType


class GoogleGeminiAdapter(InferenceProviderAbstractClass):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = genai.Client(api_key=self.api_key)

    def set_model(self, model_name=None):
        self.model = "gemini-2.5-flash" if model_name is None else model_name
        return self

    def set_system_prompt(self, system_prompt=None):
        self.system_prompt = system_prompt
        return self

    def set_user_prompt(self, user_prompt=None):
        self.user_prompt = user_prompt
        return self

    def get_response(self) -> str:
        try:
            self.response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(system_instruction=self.system_prompt, temperature=0.1),
                contents=self.user_prompt
            )
            return self.response.text.strip()
        except Exception as e:
            raise e
