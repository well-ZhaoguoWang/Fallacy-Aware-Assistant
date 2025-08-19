import json

from ask_deepseek import ask_deepseek
from tools.deepseek_service.outlines import (
    provincial_company_outline,
    data,
    group_company_outline,
)


def detect_intent(_user_input, _outline_list):
    prompt = """
    # Role
    You are an "intent detector" that determines the user's current purpose.

    # Task
    1) Read the user input.
    2) Decide whether the input indicates a need for **data analysis or formal report writing**.
       - If **yes** (writing intent) → go to Step 3
       - If **no** (small talk / other) → go to Step 4
    3) Writing intent:
       - From the following [Outline List], choose an outline that satisfies the user's request.
       - If no outline fully matches, output **"Other Outline"** (this is rewarded).
       - Distinguish whether the writing intent is **Provincial Company (incl. municipalities)** vs **Group Company**.
       - Output **JSON only**: any key name is fine (e.g., "writing_intent"), and the value must be:
         **[true, <Outline Name>, "Provincial Company" | "Group Company"]**
    4) Small talk / other intent:
       - Output **JSON only**: any key name, value must be **[false, "", ""]**

    # Outline List (names only)
    {outline_list}

    # Output examples
    - User: "Hi, nice weather today."
      Output: { "writing_intent": [false, "", ""] }
    - User: "Please write a report analyzing the Shanghai market."
      Output: { "writing_intent": [true, "<Outline Name>", "Provincial Company"] }
    - User: "Please write a nationwide traffic analysis report."
      Output: { "writing_intent": [true, "<Outline Name>", "Group Company"] }

    # User input: {user_input}
    Return JSON only.
    """

    prompt = prompt.replace("{user_input}", _user_input).replace(
        "{outline_list}", str(list(_outline_list.keys()))
    )
    result = ask_deepseek(prompt, model="r1")
    result = result.replace("```", "").replace("json", "").strip()
    try:
        ans = json.loads(result)
    except json.JSONDecodeError:
        return [False, "", ""]
    return ans.get("writing_intent", [False, "", ""])


def gen_outline(_user_input, _outline_list):
    prompt = """
    # Role
    You are a "structured outline generator" that, given a recommended outline and new user needs,
    outputs a hierarchical, field-complete **JSON** outline.

    # Input
    1) [Recommended Outline]: {outline}
    2) [User Need]: {user_need}
    3) [Available Metrics]: {data}

    # Procedure
    1) **Read the existing outline**
       - Understand its hierarchy, naming style, and field meanings.
       - Identify parts to reuse or extend.
    2) **Parse the user need**
       - Extract key topics, metrics, methods, pain points.
       - Decide whether to add new levels/sections.
    3) **Generate a new outline** (output **JSON only**, no explanations):
       - Base structure should follow the "reference format".
       - **id**: start from 1 and increment; if reusing an old item you may keep its id.
       - **parentID**: null for root; for children, set to the parent's id.
       - **level**: corresponds to depth (1, 2, 3…).
       - **title**: concise, with key info (≤ 20 characters).
       - **content**: may be empty or a brief summary.
       - **principle**: one-sentence analysis approach / writing focus.
       - **info_needed**: list the data/info needed (key = description, value = field name or "fill manually").
       - **methods**: choose only from [MoM, YoY, ranking, share calculation, variance analysis, correlation analysis].
         Using methods outside this list is penalized.

    # Output example
    [
      {
        "id": 1,
        "parentID": null,
        "title": "Network scale analysis",
        "level": "1",
        "content": "",
        "principle": "Count CT/CU 4G/5G sites and sharing ratio; split macro/indoor/low-band; tabulate inter-city differences.",
        "info_needed": [
          {"Number of gNBs": "gnbNums"},
          {"Number of site-sets": "setGnbNums"},
          {"RRU/AAU count": "rruNums"},
          {"Shared site-sets": "shareSetGnbNums"},
          {"Share of site-sets": "shareSetGnbRate"},
          {"Low-band site scale": "fill manually"}
        ],
        "methods": "ranking, share calculation"
      }
    ]

    # Constraints
    - Output **JSON only**. No extra text.
    """

    user_intent = detect_intent(_user_input, _outline_list)
    if not user_intent[0]:  # not a writing intent
        return {"error": "The user input does not involve writing intent or data analysis."}
    else:
        # user_intent = [True, outline_name, "Provincial Company" | "Group Company"]
        if user_intent[1] == "Other Outline":
            if user_intent[2] == "Provincial Company":
                _outline = provincial_company_outline
            else:
                _outline = group_company_outline
            prompt = (
                prompt.replace("{outline}", str(_outline))
                .replace("{user_need}", _user_input)
                .replace("{data}", str(list(data.keys())))
            )
            result = ask_deepseek(prompt, model="r1")
            result = result.replace("```", "").replace("json", "").strip()
            try:
                ans = json.loads(result)
                return ans
            except json.JSONDecodeError:
                return {"code": "0", "res": "Outline generation failed: invalid JSON or incomplete content."}
        else:
            this_outline = _outline_list.get(user_intent[1], group_company_outline)
            return {"code": "1", "res": this_outline}


if __name__ == "__main__":
    outline_list = {
        "Provincial Company Traffic Analysis Outline": provincial_company_outline,
        "Group Company Traffic Analysis Outline": group_company_outline,
        "Other Outline": None,
    }
    while True:
        user_input = input("Enter your request (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        outline = gen_outline(user_input, outline_list)
        print(outline)
