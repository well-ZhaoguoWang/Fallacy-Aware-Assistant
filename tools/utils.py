import json
from pathlib import Path


def load_json(filepath: str) -> dict:
    """
    读取 JSON 文件，返回字典对象。
    如果文件不存在或格式错误，将抛出异常。
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"❌ 找不到文件：{filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

