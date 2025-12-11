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

    pattern = r"```python(.*?)```"
    match = re.search(pattern, raw_text, re.DOTALL)

    if match:
        clean_code = match.group(1).strip()
    else:
        # Fallback
        clean_code = raw_text

    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_code)

    return file_path