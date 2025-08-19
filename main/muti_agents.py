from __future__ import annotations

import json
import textwrap
from typing import Dict, List, Any, Protocol

import setting
from src.fallacies_principles import fallacy_dict
from tools.deepseek_service.ask_deepseek import ask_deepseek
from tools.search_api.serp import search_google
from tools.utils import load_json

# --------------------------------------------------------------------------- #
# 0.  Basic configuration                                                     #
# --------------------------------------------------------------------------- #
DEFAULT_LANGUAGE = setting.language

# FALLACIES: list[dict[str, str]] = [
#     # --- A ---
#     {"id": "abusive_ad_hominem", "label": "Abusive Ad Hominem"},
#     {"id": "ad_populum", "label": "Ad Populum (Appeal to Majority)"},
#     {"id": "appeal_to_authority", "label": "Appeal to Authority"},
#     {"id": "appeal_to_nature", "label": "Appeal to Nature"},
#     {"id": "appeal_to_tradition", "label": "Appeal to Tradition"},
#     {"id": "appeal_to_angry", "label": "Appeal to Anger"},
#     {"id": "appeal_to_fear", "label": "Appeal to Fear"},
#     {"id": "appeal_to_pity", "label": "Appeal to Pity"},
#     {"id": "appeal_to_positive_emotion", "label": "Appeal to Positive Emotion"},
#     {"id": "appeal_to_ridicule", "label": "Appeal to Ridicule"},
#     {"id": "appeal_to_worse_problems", "label": "Appeal to Worse Problems"},
#     {"id": "appeal_to_purity", "label": "Appeal to Purity (No True Scotsman)"},
#     {"id": "appeal_to_novelty", "label": "Appeal to Novelty"},
#     {"id": "appeal_to_consequences", "label": "Appeal to Consequences"},
#     {"id": "appeal_to_emotion", "label": "Appeal to Emotion"},  # general catch-all
#
#     # --- B / C ---
#     {"id": "burden_shifting", "label": "Shifting the Burden of Proof"},
#     {"id": "causal_oversimplification", "label": "Causal Oversimplification"},
#     {"id": "cherry_picking", "label": "Cherry Picking (Texas Sharpshooter)"},
#     {"id": "circular_reasoning", "label": "Circular Reasoning"},
#     {"id": "complex_question", "label": "Loaded / Complex Question"},
#     {"id": "composition", "label": "Fallacy of Composition"},
#     {"id": "correlation_causation", "label": "Correlation ≠ Causation"},
#
#     # --- D / E / F ---
#     {"id": "division", "label": "Fallacy of Division"},
#     {"id": "equivocation", "label": "Equivocation"},
#     {"id": "false_analogy", "label": "False Analogy"},
#     {"id": "false_causality", "label": "False Causality"},
#     {"id": "false_dilemma", "label": "False Dilemma"},
#     {"id": "false_equivalence", "label": "False Equivalence"},
#
#     # --- G / H ---
#     {"id": "genetic_fallacy", "label": "Genetic Fallacy"},
#     {"id": "guilt_by_association", "label": "Guilt by Association"},
#     {"id": "hasty_generalization", "label": "Hasty Generalization"},
#
#     # --- M / P ---
#     {"id": "moving_the_goalposts", "label": "Moving the Goalposts"},
#     {"id": "poisoning_the_well", "label": "Poisoning the Well"},
#     {"id": "post_hoc", "label": "Post Hoc"},
#
#     # --- R / S / T ---
#     {"id": "red_herring", "label": "Red Herring"},
#     {"id": "slippery_slope", "label": "Slippery Slope"},
#     {"id": "special_pleading", "label": "Special Pleading"},
#     {"id": "straw_man", "label": "Straw Man"},
#     {"id": "sunk_cost", "label": "Sunk Cost"},
#     {"id": "tone_policing", "label": "Tone Policing"},
#     {"id": "tu_quoque", "label": "Tu Quoque"},
#     {"id": "two_wrongs", "label": "Two Wrongs Make a Right"},
# ]
FALLACIES: List[Dict[str, Any]] = [
    {"id": "appeal_to_authority", "label": "Appeal to Authority"},
    {"id": "appeal_to_majority", "label": "Appeal to Majority"},
    {"id": "appeal_to_nature", "label": "Appeal to Nature"},
    {"id": "appeal_to_tradition", "label": "Appeal to Tradition"},
    {"id": "appeal_to_worse_problems", "label": "Appeal to Worse Problems"},
    {"id": "false_dilemma", "label": "False Dilemma"},
    {"id": "hasty_generalization", "label": "Hasty Generalization"},
    {"id": "slippery_slope", "label": "Slippery Slope"},
    {"id": "ad_hominem", "label": "Ad Hominem"},
    {"id": "straw_man", "label": "Straw Man"},
    {"id": "red_herring", "label": "Red Herring"},
    {"id": "tu_quoque", "label": "Tu Quoque"},
    {"id": "circular_reasoning", "label": "Circular Reasoning"},
    {"id": "false_analogy", "label": "False Analogy"},
    {"id": "post_hoc", "label": "Post Hoc"},
    {"id": "correlation_causation", "label": "Correlation ≠ Causation"},
    {"id": "appeal_to_emotion", "label": "Appeal to Emotion"},
    {"id": "appeal_to_ignorance", "label": "Appeal to Ignorance"},
]

# --------------------------------------------------------------------------- #
# 1.  Agent protocol                                                          #
# --------------------------------------------------------------------------- #
class Agent(Protocol):
    name: str

    def run(self, **kwargs) -> Any: ...


# --------------------------------------------------------------------------- #
# 2.  Concrete agent implementations                                          #
# --------------------------------------------------------------------------- #
class FallacyDetectorAgent:
    name = "FallacyDetector"
    principle = str(fallacy_dict)
    #
    PROMPT_TEMPLATE = textwrap.dedent("""
        You are a logical comment analysis assistant. Please respond in {language}.

        Read the news background and the comment below, and determine whether the comment contains any of the following logical fallacies:
        {fallacy_list}

        Detailed explanations of each fallacy:
        {fallacies}

        Output JSON:
        {{
          "exists": <bool>,               # Whether a logical fallacy exists
          "fallacy_id": "<id or null>",   # Must be one of {ids}
          "reason": "<brief reason, in the same language as above>"
        }}
        News background:
        <<NEWS>>
        {news}

        Comment:
        <<COMMENT>>
        {comment}
    """).strip()

    def run(self, news: str, comment: str, language: str = DEFAULT_LANGUAGE, fallacies=FALLACIES) -> Dict[str, Any]:
        ids = [f["id"] for f in fallacies]
        prompt = self.PROMPT_TEMPLATE.format(
            language=language,
            fallacy_list=", ".join(ids),
            ids="|".join(ids),
            news=news,
            comment=comment,
            fallacies=fallacy_dict,
        )
        raw = ask_deepseek(prompt, language=language, model=setting.detect_model)
        raw = raw.replace("```", "").replace("json", "")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"exists": False, "fallacy_id": None, "reason": ""}


class EvidenceCollectorAgent:
    name = "EvidenceCollector"

    def run(self, fallacy_id: str | None, comment: str, news: str,
            language: str = DEFAULT_LANGUAGE) -> List[str]:
        if not fallacy_id:
            return []

        f_desc = ""
        for f in FALLACIES:
            if f["id"] == fallacy_id:
                f_desc = fallacy_dict.get(f["label"], "")
                break

        prompt = (
            f"Please respond in {language}.\n"
            "The following comment contains a logical fallacy:\n"
            f"- Type: {fallacy_id}\n"
            f"- Fallacy explanation: {f_desc}\n"
            f"- Comment: {comment}\n"
            f"- News background: {news}\n"
            "Please analyze what kind of keywords would help verify that this judgment is correct.\n"
            "Generate 1 commonly used search keyword for a search engine that would help prove the comment belongs to this fallacy type.\n"
            "Output only the keyword."
        )
        keyword = ask_deepseek(prompt, language=language, model=setting.evidence_model).strip()
        hits = search_google(keyword, language=language)

        if not hits:
            return []
        if hits.get("answerBox"):
            return [hits["answerBox"]]
        return hits.get("organic", [])[:2]


class AdviceAgent:
    name = "AdviceAgent"
    PROMPT_TEMPLATE = textwrap.dedent("""
        Please respond in {language}.

        You are a master of logic and an experienced psychologist. 
        Your goal is to help the user refine reasoning without confrontation or coercion. 
        Preserve user autonomy, avoid shaming, and prefer collaborative language. 
        Ground suggestions in evidence when available.. 
        You found a logical fallacy in a comment:
        - Type: {fallacy_label}
        - Reason: {reason}

        Supporting material:
        {evidence}

        In ≤100 words, write a friendly suggestion to the commenter, following these rules:
        1. Acknowledge their emotion or concern first.
        2. Point out the specific fallacy and give evidence.
        3. Attach evidence as hyperlinks in HTML suitable for front-end rendering, e.g., <a href=\"url\">xxx</a>. Output only the body of the suggestion.
        4. Keep it as a gentle, persuasive nudge.
        
    """).strip()
#-----------------------------------------#
    #     - Voice & Tone: warm, tactful, collaborative, and confident-but-tentative (e.g., “might,” “perhaps,” “consider”).
    #     - Length: 45–120 words total.
    #     - Content order (recommended):
    #     1) Brief empathy/acknowledgment.
    #     2) Name the issue in plain words linked to {type} (avoid jargon unless helpful).
    #     3) One-sentence rationale anchored in {reasoning}.
    #     4) If suitable, weave in *one* short piece of evidence as an inline HTML link.
    #     5) Offer a concise, improved rephrase or next step.
    #     6) End with an open, non-leading question or gentle invitation to reconsider.
    #     - Do:
    #         - Be specific and actionable.
    #         - Keep the focus on the claim, not the person.
    #         - Use a single, high-quality citation if {evidence_list} contains a strong item.
    #     - Don’t:
    #         - Fabricate facts or links.
    #         - Sound accusatory, sarcastic, or absolute.
    #         - Overwhelm with multiple citations or long quotes.
#-----------------------------------------#
    def run(self, comment: str, fallacy_id: str | None, reason: str | None,
            evidence: List[str], language: str = DEFAULT_LANGUAGE) -> str:
        label = next((f["label"] for f in FALLACIES if f["id"] == fallacy_id), "Unknown type")
        prompt = self.PROMPT_TEMPLATE.format(
            language=language,
            fallacy_label=label,
            reason=reason or "",
            evidence="\n".join(map(str, evidence)) or "None",
        )
        return ask_deepseek(prompt, language=language, model=setting.suggestion_model).strip()


# --------------------------------------------------------------------------- #
# 3.  Orchestrator                                                            #
# --------------------------------------------------------------------------- #
class CommentModerator:
    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        self.language = language
        self.detector = FallacyDetectorAgent()
        self.collector = EvidenceCollectorAgent()
        self.advisor = AdviceAgent()

    def moderate(self, news: str, comment: str) -> str | Any:
        detection = self.detector.run(news=news, comment=comment, language=self.language)
        fallacy_id = detection.get("fallacy_id")
        reason = detection.get("reason", "")

        # If you don't want to use evidence collection, pass an empty list:
        evidence = []  # Or enable: self.collector.run(fallacy_id, comment, news, language=self.language)

        if detection.get("exists"):
            # Get the fallacy label
            fallacy_label = next(
                (f["label"] for f in FALLACIES if f["id"] == fallacy_id),  # Parentheses must be correctly closed here.
                "Unknown Fallacy"
            )
            # Generate a friendly suggestion
            advice = self.advisor.run(comment, fallacy_id, reason, evidence, language=self.language)
            return f"{fallacy_label}\n\n{advice}"
        else:
            return "No obvious fallacy detected"

        # return {
        #     "fallacy": next((f["label"] for f in FALLACIES if f["id"] == fallacy_id), None)
        #     if detection.get("exists") else None,
        #     "reason": reason,
        #     "evidence": evidence,
        #     "advice": advice
        # }

if __name__ == "__main__":
    moderator = CommentModerator()
    cocolafa_data = load_json("../data/cocolafa/test.json")
    news_demo = cocolafa_data[0]
    title = news_demo["title"]
    link = news_demo["link"]
    for comment in news_demo["comments"]:
        comment_demo = comment["comment"].strip()
        fall = comment.get("fallacy", "")
        print(f"\nGround-truth fallacy type: {fall}")
        result = moderator.moderate(news_demo, comment_demo)
        print("\n" + title + "\n" + link + "\nComment:\n" + comment_demo + "\nResult:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        break
