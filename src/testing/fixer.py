from typing import Optional, Any, Generator

from src.utils import call_llm
from src.testing.prompts import FIXER_PROMPT, LOGIC_REVIEW_PROMPT, LOGIC_FIXER_PROMPT
from src.generation.file_utils import save_code_to_file
from src.testing.fuzzer import run_fuzz_test
from config import config
import os
import ast

def static_code_check(file_path: str) -> tuple[bool, str]:
    """
    Use Python ast module, inspecting the syntax errors.
    @:return (syntax validity, error message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True, "語法檢查通過 ✅"
    except SyntaxError as e:
        return False, f"語法錯誤 ❌: {e}"
    except Exception as e:
        return False, f"其他錯誤 ❌: {e}"

def game_logic_check(gdd:str ,file_path: str, provider: str = "openai", model: str = "gpt-4o-mini") -> tuple[bool, str]:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    prompt = LOGIC_REVIEW_PROMPT.format(code=code)
    response = call_llm("You are a code logic reviewer.",
             prompt,
             provider=provider,
             model=model
    )
    print(f"[Member 3]: response of game_logic_check {response}")
    if "PASS" in response.upper() : return True, ""
    return False, response

def run_fix(file_path: str, error_message: str, provider: str = "openai"
                 , model: str  = "gpt-4o-mini", fix_type: str="syntax", gdd: Optional[str]="") -> tuple[str | None, str]:
    """
    Auto Fix Loop: Read Codes -> Submit Errors -> Get new codes -> save
    The first return is the path to the fixed file.
    The second return is the result message.
    """
    print(f"[Member 3] 正在嘗試修復代碼... (Error: {error_message[:50]}...)")

    # Read the broken codes
    if not os.path.exists(file_path):
        return None, "找不到原始代碼檔案"

    with open(file_path, "r", encoding="utf-8") as f:
        broken_code = f.read()

    response: str  = ""

    if fix_type == "syntax":
        # Insert the codes to the prompt
        fix_syntax_full_prompt: str = FIXER_PROMPT.format(code=broken_code, error=error_message)
        # Call LLM for fixing
        response = call_llm("You are a Code error Fixer.", fix_syntax_full_prompt, provider=provider, model=model)
    elif fix_type == "logic":
        fix_logic_full_prompt: str = LOGIC_FIXER_PROMPT.format(code=broken_code, error=error_message, gdd=gdd)
        response = call_llm("You are a code logics fixer.", fix_logic_full_prompt, provider=provider, model=model)

    # Save the fixed files (truncate)
    output_dir: str = os.path.dirname(file_path)
    new_path: str | None = save_code_to_file(response, output_dir=output_dir)

    if new_path:
        return new_path, response
    else:
        return None, response


def run_fix_loop(gdd: str, file_path: str, provider: str = "openai",
                 model: str = "gpt-4o-mini") -> Generator[str, None, None]:
    """
    Generator function for SSE (Server-Sent Events).
    Yields strings in the format: "data: <message>\n\n"
    """
    yield f"data: [Member 3] 收到需求，開始驗證: {os.path.basename(file_path)}\n\n"

    max_retries: int = 3
    game_is_valid = False
    error_msg = ""

    while (not game_is_valid) and (max_retries > 0):
        syntax_is_valid, error_msg = static_code_check(file_path)
        if not syntax_is_valid:
            yield f"data: ❌ 語法錯誤: {error_msg} (嘗試修復中...)\n\n"
            print(f"[Member3]: ❌ 語法錯誤: {error_msg}")

            file_path, error_msg = run_fix(file_path, error_msg, provider, model, "syntax")
            max_retries -= 1
            continue

        yield "data: ✅ 語法正確\n\n"

        logic_is_valid, error_msg = game_logic_check(gdd, file_path, provider, model)
        if not logic_is_valid:
            yield f"data: ❌ 邏輯錯誤: {error_msg} (嘗試修復中...)\n\n"
            print(f"[Member3]: ❌ 邏輯錯誤: {error_msg}")

            file_path, error_msg = run_fix(file_path, error_msg, provider, model, "logic", gdd)
            max_retries -= 1
            continue

        yield "data: ✅ 邏輯正確\n\n"

        fuzz_passed, error_msg = run_fuzz_test(file_path, config.FUZZER_RUNNING_TIME)
        if not fuzz_passed:
            yield f"data: ❌ 運行時錯誤 (Fuzzer): {error_msg} (嘗試修復中...)\n\n"
            print(f"[Member3]: ❌ 運行時錯誤 (Fuzzer): {error_msg}")

            file_path, error_msg = run_fix(file_path, error_msg, provider, model, "logic", gdd)
            max_retries -= 1
            continue

        yield "data: ✅ 運行功能正確\n\n"

        game_is_valid = True

    # The format let js can detect finished
    if game_is_valid:
        yield "data: RESULT_SUCCESS: 程式碼通過所有驗證！\n\n"
    else:
        yield "data: RESULT_FAIL: 已達最大重試次數，驗證失敗。\n\n"