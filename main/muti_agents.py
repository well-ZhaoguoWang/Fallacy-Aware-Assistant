"""
使用示例
--------
moderator = CommentModerator()
result = moderator.moderate(news_text, comment_text)
print(result["fallacy"])   # 如 "Appeal to Authority（诉诸权威）"
print(result["advice"])    # 给评论者的温和建议
"""

from __future__ import annotations

from pydoc import describe
from typing import Dict, List, Any, Protocol
import json
import textwrap

from tools.deepseek_service.ask_deepseek import ask_deepseek
from tools.search_api.fetch_news import fetch_news_main_text
from tools.search_api.serp import search_google
from src.fallacies_principles import fallacy_dict

# --------------------------------------------------------------------------- #
# 0.  逻辑谬误目录（如需扩展可在此添加）                                       #
# --------------------------------------------------------------------------- #
from tools.utils import load_json

FALLACIES: List[Dict[str, Any]] = [
    {"id": "appeal_to_authority", "label": "Appeal to Authority（诉诸权威）"},
    {"id": "appeal_to_majority", "label": "Appeal to Majority（诉诸多数）"},
    {"id": "appeal_to_nature", "label": "Appeal to Nature（诉诸自然）"},
    {"id": "appeal_to_tradition", "label": "Appeal to Tradition（诉诸传统）"},
    {"id": "appeal_to_worse", "label": "Appeal to Worse Problems（诉诸更糟）"},
    {"id": "false_dilemma", "label": "False Dilemma（假两难）"},
    {"id": "hasty_generalization", "label": "Hasty Generalization（草率概括）"},
    {"id": "slippery_slope", "label": "Slippery Slope（滑坡谬误）"},
]


# --------------------------------------------------------------------------- #
# 1.  Agent 协议                                                             #
# --------------------------------------------------------------------------- #

class Agent(Protocol):
    """所有智能体需遵循的最小接口"""
    name: str

    def run(self, **kwargs) -> Any: ...


# --------------------------------------------------------------------------- #
# 2.  具体智能体实现                                                         #
# --------------------------------------------------------------------------- #

class FallacyDetectorAgent:
    """
    负责调用大模型判断评论是否含有逻辑谬误，
    若存在，则输出谬误类型及简要原因。
    """
    name = "FallacyDetector"
    principle = str(fallacy_dict)
    PROMPT_TEMPLATE = textwrap.dedent(
        """
        你是逻辑评论分析助手。请阅读下面新闻背景与评论，判断评论是否包含以下任一逻辑谬误：
        {fallacy_list}
        
        各类谬误详细解释如下：
        {fallacies}

        输出 JSON：
        {{
          "exists": <bool>,              # 是否存在逻辑谬误
          "fallacy_id": "<id 或 null>",  # 只能取 {ids} 中的值
          "reason": "<中文简要原因>"
        }}

        新闻背景：
        <<NEWS>>
        {news}

        评论：
        <<COMMENT>>
        {comment}
    """).strip()

    def run(self, news: str, comment: str) -> Dict[str, Any]:
        ids = [f["id"] for f in FALLACIES]
        prompt = self.PROMPT_TEMPLATE.format(
            fallacy_list=", ".join(ids),
            ids="|".join(ids),
            news=news,
            comment=comment,
            fallacies=fallacy_dict,
        )
        raw = ask_deepseek(prompt)  # 调用大模型
        # TODO 这里后面得加一个json schema 防止解析失败
        raw = raw.replace("json", "")
        raw = raw.replace("```", "")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # 若解析失败，返回默认结果
            return {"exists": False, "fallacy_id": None, "reason": ""}


class EvidenceCollectorAgent:
    """
    若检测到逻辑谬误，使用搜索接口查找 1~2 条相关科普/解释，方便引用。
    """
    name = "EvidenceCollector"
    SEARCH_TEMPLATE = "{fallacy_cn} 逻辑谬误 解释 示例"

    def run(self, fallacy_id: str | None, comment, news) -> List[str]:
        if not fallacy_id:
            return []
        f_desc = ""
        for f in FALLACIES:
            if f.get("id") == fallacy_id:
                label = f.get("label")
                f_desc = fallacy_dict.get(label)
        prompt = (
            "下面的评论发生了逻辑谬误，"
            f"\n类型为{fallacy_id}，谬误解释：{str(f_desc)}"
            f"\n谬误原文为：{comment}"
            f"\n谬误背景信息为：{news}"
            "下面你需要生成1个搜索关键词来佐证这确实是一个谬误"
            "请仅输出搜索关键词")
        keyword = ask_deepseek(prompt)

        hits = search_google(keyword)  # 加个language入参即可改语言
        if len(hits) == 0:
            return []
        else:
            if hits.get("answerBox", ""):
                return [hits.get("answerBox")]
            else:
                ans = hits.get("organic")
                return ans[:2]


class AdviceAgent:
    """
    根据检测结果，给评论者提供<120 字>以内的温和建议。
    """
    name = "AdviceAgent"

    PROMPT_TEMPLATE = textwrap.dedent("""
        你是一位友善的评论区版主。请在不激起防御心的前提下，
        对下面评论给出暖心建议（≤120 字）：
        1. 先肯定对方情绪或关注点；
        2. 委婉指出其可能涉及的逻辑谬误：{fallacy_label}；
        3. 提出一种友好的查证或思考方式；
        避免使用“你错了”等指责性语句，尽量使用“也许你可以…”等表达。
        评论：
        {comment}
        可以佐证的网络查询结果如下
        {evidence}
        请输出暖心建议
    """).strip()

    def run(self, comment: str, fallacy_id: str | None, evidence) -> str:
        label = next((f["label"] for f in FALLACIES if f["id"] == fallacy_id), "未知类型")
        prompt = self.PROMPT_TEMPLATE.format(fallacy_label=label, comment=comment, evidence=evidence)
        return ask_deepseek(prompt)


# --------------------------------------------------------------------------- #
# 3.  Orchestrator / 调度器                                                  #
# --------------------------------------------------------------------------- #

class CommentModerator:
    """
    高层调度器：按顺序调用各智能体，返回统一结构化结果。
    """

    def __init__(self) -> None:
        self.detector = FallacyDetectorAgent()
        self.collector = EvidenceCollectorAgent()
        self.advisor = AdviceAgent()

    def moderate(self, news: str, comment: str) -> Dict[str, Any]:
        detection = self.detector.run(news=news, comment=comment)
        fallacy_id = detection.get("fallacy_id")

        evidence = self.collector.run(fallacy_id, comment, news)
        advice = (
            self.advisor.run(comment=comment, fallacy_id=fallacy_id, evidence=evidence)
            if detection.get("exists") else
            "未发现明显逻辑问题"
        )

        return {
            "fallacy": next((f["label"] for f in FALLACIES if f["id"] == fallacy_id), None)
            if detection.get("exists") else None,
            "reason": detection.get("reason"),
            "evidence": evidence,
            "advice": advice
        }


# --------------------------------------------------------------------------- #
# 4.  测试示例（正式部署时请移除此段）                                        #
# --------------------------------------------------------------------------- #


if __name__ == "__main__":
    moderator = CommentModerator()
    cocolafa_data = load_json("../data/cocolafa/dev.json")
    news_demo = cocolafa_data[0]
    title = news_demo["title"]
    link = news_demo["link"]
    content = fetch_news_main_text(link)
    for comment in news_demo["comments"]:
        comment_demo = comment["comment"].strip()
        fall = comment.get("fallacy", "")
        print(f"\n谬误类型：{fall}")
        result = moderator.moderate(news_demo, comment_demo)
        print("\n" + title + "\n" + link + "\n评论：\n" + comment_demo + "\n结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
