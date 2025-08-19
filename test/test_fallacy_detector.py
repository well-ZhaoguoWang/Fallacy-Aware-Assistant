# test_fallacy_detector.py
# ------------------------------------------------------------
# Evaluate FallacyDetectorAgent accuracy on the COCOlafa test set
# ------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from tools.utils import load_json
from main.muti_agents import CommentModerator

FALLACIES: List[Dict[str, Any]] = [
    {"id": "appeal_to_authority", "label": "Appeal to Authority"},
    {"id": "appeal_to_majority", "label": "Appeal to Majority"},
    {"id": "appeal_to_nature", "label": "Appeal to Nature"},
    {"id": "appeal_to_tradition", "label": "Appeal to Tradition"},
    {"id": "appeal_to_worse_problems", "label": "Appeal to Worse Problems"},
    {"id": "false_dilemma", "label": "False Dilemma"},
    {"id": "hasty_generalization", "label": "Hasty Generalization"},
    {"id": "slippery_slope", "label": "Slippery Slope"},
]

# ------------------------- CLI args --------------------------
parser = argparse.ArgumentParser(
    description="Evaluate logical fallacy detection accuracy on a test set."
)
parser.add_argument(
    "--test-file",
    default="../data/cocolafa/test.json",
    help="Path to the COCOlafa-style test set",
)
parser.add_argument(
    "--language",
    default="en",
    choices=["zh", "en"],
    help="Language used by the detector prompt",
)
args = parser.parse_args()


def _normalize_fallacy(s: Any) -> str | None:
    """Normalize fallacy labels/ids for comparison: lowercase, collapse spaces,
    convert '_' and '-' to spaces. Returns None if empty."""
    if s is None:
        return None
    s = str(s).strip().lower()
    if not s:
        return None
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s


# ------------------------- Main ------------------------------
def main(test_path: str, language: str) -> None:
    # 1) Load data
    data: List[Dict[str, Any]] = load_json(test_path)
    if not data:
        raise FileNotFoundError(f"❌ Unable to read file or file is empty: {test_path}")

    moderator = CommentModerator(language=language)

    total, correct = 0, 0
    details: List[Dict[str, Any]] = []

    print(f"🔍 Starting evaluation. Number of news items: {len(data)}")

    # 2) Iterate over news items & comments
    for sample in data:
        # Build news text from fields (adjust as needed for your dataset schema)
        news_text = "\n".join(
            filter(None, [sample.get("title", ""), sample.get("content", "")])
        )

        for com in sample.get("comments", []):
            gt_fallacy_raw = com.get("fallacy") or None  # ground-truth label
            comment_txt = (com.get("comment") or "").strip()

            # Only run the detector (faster)
            det_res = moderator.detector.run(
                news=news_text, comment=comment_txt, language=language, fallacies=FALLACIES
            )
            pred_id_raw = det_res["fallacy_id"] if det_res.get("exists") else "none"

            # Normalize for comparison
            pred_id = _normalize_fallacy(pred_id_raw)
            gt_fallacy = _normalize_fallacy(gt_fallacy_raw)

            total += 1
            is_correct = (pred_id or None) == gt_fallacy
            if is_correct:
                correct += 1

            # Save detailed record for error analysis
            details.append(
                {
                    "comment": comment_txt,
                    "ground_truth": gt_fallacy_raw,
                    "prediction": pred_id_raw,
                    "correct": is_correct,
                    "detector_reason": det_res.get("reason", ""),
                }
            )

    # 3) Aggregate stats
    accuracy = correct / total if total else 0.0
    print(
        f"\n✅ Evaluation complete\n"
        f"   • Total comments: {total}\n"
        f"   • Correct predictions: {correct}\n"
        f"   • Accuracy: {accuracy:.2%}\n"
    )

    # 4) Save details
    out_path = Path("fallacy_detection_report.json")
    out_path.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📄 Detailed comparison written to: {out_path.resolve()}")


if __name__ == "__main__":
    main(args.test_file, args.language)
