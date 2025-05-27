import json

def format_json_file(file_path: str, indent: int = 4, ensure_ascii: bool = False):
    """
    读取 JSON 文件并格式化写回，提升可读性（缩进、换行、美化）

    参数：
    - file_path (str): JSON 文件路径
    - indent (int): 缩进空格数，默认4
    - ensure_ascii (bool): 是否只保留 ASCII 字符，中文设为 False
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        print(f"✅ JSON 文件已格式化：{file_path}")

    except Exception as e:
        print(f"❌ 格式化失败：{e}")


if __name__ == "__main__":
    format_json_file("data_test.json")