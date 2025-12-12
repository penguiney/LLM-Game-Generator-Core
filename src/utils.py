import openai
from config import config

def get_client_config(provider: str) -> dict | None:
    """
    根據 Provider 回傳對應的 Client 設定 (api_key, base_url)
    支援 OpenAI 相容介面的服務 (Groq, Ollama, Mistral)
    """
    provider = provider.lower()

    if provider == "openai":
        return {
            "api_key": config.OPENAI_API_KEY,
            "base_url": None
        }
    elif provider == "groq":
        return {
            "api_key": config.GROQ_API_KEY,
            "base_url": "https://api.groq.com/openai/v1"
        }
    elif provider == "ollama":
        return {
            "api_key": config.OLLAMA_API_KEY,
            "base_url": config.OLLAMA_BASE_URL
        }
    elif provider == "mistral":
        return {
            "api_key": config.MISTRAL_API_KEY,
            "base_url": "https://api.mistral.ai/v1"
        }
    elif provider == "deepseek":
        return {
            "api_key": config.DEEPSEEK_API_KEY,
            "base_url": "https://api.deepseek.com/v1"
        }
    return None


def call_google_gemini(system_prompt: str, user_prompt: str,
                       model: str, temperature: float) -> str:
    """
    處理 Google Gemini 的特殊邏輯 (需安裝 google-generativeai)
    """
    try:
        import google.generativeai as genai
    except ImportError:
        return "Error: 請安裝 google-generativeai 套件 (pip install google-generativeai)"

    api_key: str = config.GOOGLE_API_KEY
    if not api_key:
        return "Error: 未設定 GOOGLE_API_KEY"

    try:
        genai.configure(api_key=api_key)

        generation_config: dict = {
            "temperature": temperature,
            "top_p": 0.95,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # System instructions
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_prompt
        )

        response = gemini_model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error: {str(e)}"


def call_llm(system_prompt: str, user_prompt: str, provider: str ="openai",
             model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """
    [統一入口] 支援多種 LLM Provider
    Provider: 'openai', 'groq', 'google', 'ollama', 'mistral'
    """
    provider = provider.lower()

    # --- Google Gemini ---
    if provider in ["google", "gemini"]:
        # 如果使用者傳入的是 OpenAI 的型號名稱，自動切換成 Gemini 預設型號
        if model.startswith("gpt"):
            model = "gemini-2.5-flash"
        return call_google_gemini(system_prompt, user_prompt, model, temperature)

    openai_config = get_client_config(provider)
    if not openai_config: return f"Error: 不支援的 Provider '{provider}'"

    # [FIX] 使用 .get() 避免 KeyError: 'key' 或 'api_key'
    api_key = openai_config.get("api_key")
    base_url = openai_config.get("base_url")

    # 檢查 Key 是否存在 (Ollama 除外)
    if not api_key and provider != "ollama":
        return f"Error: 請在 .env 設定 {provider.upper()}_API_KEY"

    try:
        # 初始化 OpenAI Client
        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            timeout=600,  # [FIX] 強制設定 600秒 超時
            max_tokens=8192  # [FIX] 強制設定最大 Token 數，避免 DeepSeek 截斷
        )
        return response.choices[0].message.content
    except KeyError as e:
        print(f"[LLM Config Error] Missing key: {e}")  # [FIX] 加入錯誤列印，方便除錯
        return f"Configuration Error: Missing key {str(e)}"
    except Exception as e:
        print(f"[LLM Call Error] Provider: {provider}, Error: {e}")  # [FIX] 加入錯誤列印，方便除錯
        return f"LLM Call Error ({provider}): {str(e)}"