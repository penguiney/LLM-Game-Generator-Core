import os
import re
import subprocess
import sys
import textwrap


def get_dynamic_fuzz_logic(game_file_path: str) -> str:
    """
    Try to find the dynamic fuzz logic fuzz_logic.py at the same directory level of the given game file.
    If it is not found, return default logic.
    :param game_file_path: The path to the game file
    :type game_file_path: str

    :return: The dynamic fuzz logic
    :rtype: str
    """
    dir_path = os.path.dirname(game_file_path)
    logic_path = os.path.join(dir_path, "fuzz_logic.py")

    default_logic = """
if random.random() < 0.05:
    _mx = random.randint(0, globals().get('WIDTH', 800))
    _my = random.randint(0, globals().get('HEIGHT', 600))
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (_mx, _my), 'button': 1}))

if random.random() < 0.05:
    _keys = [pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_d]
    _k = random.choice(_keys)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': _k, 'unicode': ''}))
    """

    if os.path.exists(logic_path):
        try:
            with open(logic_path, "r", encoding="utf-8") as f:
                content = f.read()
                return content
        except Exception:
            return default_logic

    return default_logic


def inject_monkey_bot(code_content: str, bot_logic: str) -> str:
    """
    Inject monkey bot code into the given code content.
    :param code_content: The code content
    :type code_content: str

    :param bot_logic: The bot logic
    :type bot_logic: str

    :return: The injected code
    :rtype: str
    """

    # 1. 前處理：過濾掉會造成 Variable Shadowing 的 import 語句
    lines = bot_logic.splitlines()
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # [FIX] 如果 AI 生成了 import pygame 或 import random，直接丟棄該行
        # 因為 pygame 是全域的，random 我們會用 _monkey_random 取代
        if stripped.startswith("import pygame") or stripped.startswith("from pygame"):
            continue
        if stripped.startswith("import random"):
            continue
        filtered_lines.append(line)

    if not filtered_lines:
        filtered_lines = ["pass"]

    # 重新組合成字串
    bot_logic = "\n".join(filtered_lines)
    # 2. Handle the indent and the variable name of the bot_logic
    bot_logic = textwrap.dedent(bot_logic).strip()

    bot_logic = bot_logic.replace("random.", "_monkey_random.")

    lines = bot_logic.splitlines()
    if not lines:
        lines = ["pass"]

    indented_logic = "\n".join(["            " + line for line in lines])

    # 3. Define the injection template
    # Use "import random as _monkey_random" to avoid the conflict.
    monkey_bot_template = """
    # --- [INJECTED DYNAMIC MONKEY BOT START] ---
    if 'pygame' in globals():
        try:
            import random as _monkey_random
            # Dynamic Logic from GDD
{indented_logic}
        except Exception as _e:
            pass 
    # --- [INJECTED DYNAMIC MONKEY BOT END] ---
    """

    # Inject logic
    monkey_bot_code = monkey_bot_template.replace("{indented_logic}", indented_logic)

    # Handle the indentation
    monkey_bot_code = textwrap.dedent(monkey_bot_code).strip()

    # 4. Find injection point (Main Loop) and detect the indentation
    pattern = r"^([ \t]*)while\s+.*:"
    matches = list(re.finditer(pattern, code_content, re.MULTILINE))

    if matches:
        last_match = matches[-1]
        insertion_point = last_match.end()

        # 5. Dynamically calculate the target indentation
        current_indent = last_match.group(1)
        target_indent = current_indent + "    "

        final_block = "\n".join([target_indent + line for line in monkey_bot_code.splitlines()])

        new_code = (
                code_content[:insertion_point] +
                "\n" +
                final_block +
                code_content[insertion_point:]
        )
        return new_code

    return code_content


def run_fuzz_test(file_path: str, duration: int = 5) -> tuple[bool, str]:
    """
    Run the fuzz test
    :param file_path: The path to the game file
    :type file_path: str

    :param duration: The duration of the fuzz test
    :type duration: int

    :return: A tuple (success_flag, message)
    :rtype: tuple[bool, str]
    """
    try:
        if not os.path.exists(file_path):
            return False, "File not found"

        with open(file_path, "r", encoding="utf-8") as f:
            original_code = f.read()

        bot_logic = get_dynamic_fuzz_logic(file_path)

        fuzzed_code = inject_monkey_bot(original_code, bot_logic)

        temp_file = file_path.replace(".py", "_fuzz_temp.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(fuzzed_code)

        print(f"[Fuzzer] 正在對 {os.path.basename(file_path)} 進行 {duration} 秒的動態壓力測試...")

        # 5. Set environment variable (disable sound effects to avoid interference)
        env = os.environ.copy()
        env["SDL_AUDIODRIVER"] = "dummy"

        # 6. Run the main_fuzz_temp.py
        cmd = [sys.executable, temp_file]
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=env
        )

        try:
            stdout, stderr = process.communicate(timeout=duration)
        except subprocess.TimeoutExpired:
            process.kill()
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return True, "Fuzz Test Passed (Survived random inputs)."

        if os.path.exists(temp_file):
            os.remove(temp_file)

        if process.returncode != 0:
            error_msg = stderr
            if "Traceback" in stderr:
                error_msg = "Traceback" + stderr.split("Traceback")[-1]

            return False, f"Runtime Logic Error (Crashed): {error_msg}"

        return True, "Fuzz Test Passed."

    except Exception as e:
        return False, f"Fuzz Test Failed to Run: {str(e)}"