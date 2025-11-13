from providers.providertypes import InferenceProviderType
from providers.google_gemini_adapter import GoogleGeminiAdapter
from providers.abstract import InferenceProviderAbstractClass


class InferenceProviderFactory:
    """Factory for creating LLM provider instances"""

    _providers = {
        InferenceProviderType.GEMINI: GoogleGeminiAdapter,
    }

    @classmethod
    def create(cls, provider_type: InferenceProviderType, **kwargs) -> InferenceProviderAbstractClass:
        """Create and return an LLM provider instance"""
        provider_class = cls._providers.get(provider_type)

        if not provider_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        return provider_class(**kwargs)
