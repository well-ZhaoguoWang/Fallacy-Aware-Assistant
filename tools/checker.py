import json
from typing import Tuple, Optional

from tools.deepseek_service.ask_deepseek import ask_deepseek


def check_summary_metrics(
        metrics_text: str,
        summary_text: str,
        *,
        model_fn=ask_deepseek,
) -> Tuple[bool, Optional[str]]:
    """
    Check whether every metric referenced in `summary_text` comes from `metrics_text`.

    Parameters
    ----
    metrics_text : str
        The original list/text of metrics from the first query; may contain newlines or commas.
    summary_text : str
        The model-written summary based on `metrics_text`.
    model_fn : Callable[[str], str], optional
        The function used to call the model; defaults to the global ask_deepseek.
        TODO: replace with your server-side model dispatcher.

    Returns
    ----
    Tuple[bool, Optional[str]]
        - If validation passes, return (True, None)
        - If validation fails, return (False, new_summary)
          where new_summary is the model’s revised summary after removing hallucinated metrics.
    """
    # Build a prompt for strict validation
    prompt = f"""
You are a strict proofreading assistant. Determine whether all metrics mentioned in the summary appear in the allowed list.
-----------------------
Allowed metrics list (metrics_text):
{metrics_text}

Summary to validate (summary_text):
{summary_text}
-----------------------
If every metric referenced in the summary is present in the allowed list, output:
{{"valid": true, "revised_summary": null}}

Otherwise, delete or rewrite all “hallucinated” metrics, then return:
Requirements: If hallucinated data appears in a table, use '-' (dash) to blank it.
Requirements: If any value is wrong, correct it strictly according to the reference data.
{{"valid": false, "revised_summary": "the new summary after removing hallucinations"}}
Output JSON only, no explanations.
""".strip()

    # Call the model
    raw_reply = model_fn(prompt)

    # Parse and return (be robust)
    try:
        result = json.loads(raw_reply)
        if (
            isinstance(result, dict)
            and isinstance(result.get("valid"), bool)
            and (
                result["revised_summary"] is None
                or isinstance(result["revised_summary"], str)
            )
        ):
            return result["valid"], result["revised_summary"]
    except json.JSONDecodeError:
        pass  # fall through to error below
    import json
    from pathlib import Path
    from typing import Dict

    def load_json(filepath: str) -> dict:
        """
        Read a JSON file and return a dictionary object.
        Raises an exception if the file does not exist or the JSON is malformed.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"❌ File not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def save_json(data: Dict, path: str | Path) -> None:
        """Serialize `data` to JSON and save; ensure UTF-8 and readable indentation."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    import difflib
    from typing import List, Optional

    def closest_match(target: str, candidates: List[str]) -> Optional[str]:
        """
        Return the string in `candidates` that is most similar to `target`.
        """
        # n=1: take only the best match; cutoff=0 ensures a result as long as candidates is not empty
        matches = difflib.get_close_matches(target, candidates, n=1, cutoff=0)
        return matches[0] if matches else None

    # If the model returns an unexpected format, raise to alert the caller
    raise ValueError(f"ask_deepseek returned unexpected format: {raw_reply!r}")


if __name__ == "__main__":
    # Test case
    metrics = "Report card: Math 98, English 99, Chinese 92"
    summary = "Math was near full marks, Chinese below 80, English 99"

    valid, revised = check_summary_metrics(metrics, summary)
    print(f"Validation result: {valid}, Revised summary: {revised}")
