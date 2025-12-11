import re
from src.utils import call_llm
from src.generation.prompts import ART_PROMPT


def generate_assets(
        gdd_context: str,
        provider: str = "openai",
        model: str = "gpt-4o-mini"
) -> str:
    """
    Generate the art assets for this specific game.
    :param gdd_context: The GDD context to use
    :type gdd_context: str

    :param provider: The LLM service provider
    :type provider: str

    :param model: The LLM model to use
    :type model: str

    :return: The generated assets json
    :rtype: str
    """
    response = call_llm(ART_PROMPT, f"GDD Content:\n{gdd_context}", provider=provider, model=model)

    try:
        # Find {...} structure
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response
    except:
        return "{}"