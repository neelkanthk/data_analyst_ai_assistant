from openai import OpenAI
from google.genai import types
from providers.abstract import InferenceProviderAbstractClass


class AWSBedrockAdapter(InferenceProviderAbstractClass):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = OpenAI(
            api_key=self.api_key,  # Your Bedrock API key
            base_url=kwargs.get("base_url")
        )

    def set_model(self, model_name=None):
        self.model = "openai.gpt-oss-20b-1:0" if model_name is None else model_name
        return self

    def set_system_prompt(self, system_prompt=None):
        self.system_prompt = system_prompt
        return self

    def set_user_prompt(self, user_prompt=None):
        self.user_prompt = user_prompt
        return self

    def get_response(self) -> str:
        try:
            self.response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_prompt}
                ],
                temperature=0.1
            )
            return self.response.choices[0].message.content.strip()
        except Exception as e:
            raise e
