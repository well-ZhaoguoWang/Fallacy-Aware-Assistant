import json

def format_json_file(file_path: str, indent: int = 4, ensure_ascii: bool = False):
    """
    Read a JSON file and write it back in a formatted, more readable style (indentation, new lines, pretty-printing).

    Parameters:
    - file_path (str): Path to the JSON file
    - indent (int): Number of spaces for indentation (default: 4)
    - ensure_ascii (bool): Whether to escape non-ASCII characters; set to False to keep characters like Chinese
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        print(f"✅ JSON file formatted: {file_path}")

    except Exception as e:
        print(f"❌ Formatting failed: {e}")


if __name__ == "__main__":
    format_json_file("data_test.json")
