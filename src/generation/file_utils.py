import re
import os


def save_code_to_file(
        raw_text: str,
        output_dir: str = "output",
        filename: str = "main.py"
) -> str:

    """
    Detect the code section in the raw_text and save the code to file.
    :param raw_text: The raw text containing the code
    :type raw_text: str

    :param output_dir: The output directory
    :type output_dir: str

    :param filename: The name of the file
    :type filename: str

    :return: The complete file path
    :rtype: str
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        # 1. 嘗試匹配完整的程式碼區塊 (最理想情況)
    pattern_complete = r"```python(.*?)```"
    match = re.search(pattern_complete, raw_text, re.DOTALL)

    clean_code = ""
    is_truncated = False

    if match:
        clean_code = match.group(1).strip()
    else:
        # 2. Fallback: 匹配從 ```python 開始到結尾的所有內容 (截斷情況)
        pattern_partial = r"```python(.*)"
        match_partial = re.search(pattern_partial, raw_text, re.DOTALL)

        if match_partial:
            clean_code = match_partial.group(1).strip()
            is_truncated = True
        else:
            # 3. Last Resort: 純代碼模式
            if "import pygame" in raw_text:
                clean_code = raw_text.strip()
            else:
                print("Warning: 無法解析出有效的 Python 代碼")

    # [FIX] 針對截斷代碼進行緊急修補
    if is_truncated:
        print(f"[Warning] 偵測到 {filename} 被 LLM 截斷，正在嘗試修補...")
        clean_code += "\n\n# --- [AUTO-FIX: Truncated Code] ---\n"

        # 如果截斷發生在 class 或 function 內部，簡單補一個 pass 避免 IndentationError
        # (這很簡陋，但比崩潰好)
        if clean_code.strip().endswith(":"):
            clean_code += "    pass\n"

        # 嘗試補上 main 執行區塊，讓程式至少能跑起來測試
        if "def main():" in clean_code and 'if __name__ == "__main__":' not in clean_code:
            # 如果 main 函式也沒寫完，先試著關閉 main
            clean_code += "\n    # Force closing main due to truncation\n    pass\n    pygame.quit()\n    sys.exit()\n\n"
            clean_code += 'if __name__ == "__main__":\n    try:\n        main()\n    except Exception as e:\n        print(f"Truncation Error: {e}")'

    # 存檔
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_code)

    return file_path