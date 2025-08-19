from openai import OpenAI
import setting

client = OpenAI(
    # Read your Ark (DeepSeek) API key from environment/config
    api_key=setting.deepseek_api_key,
    base_url=setting.deepseek_api_url,
)

# Optional: example tool declarations (function calling)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather information for a city.",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Query news articles by keywords.",
            "parameters": {
                "type": "object",
                "properties": {"keywords": {"type": "string"}},
                "required": ["keywords"],
            },
        },
    },
]


def ask_deepseek(_query, model="r1", history=None, language=setting.language):
    """
    Send a prompt to DeepSeek (Ark) chat API with streaming output.
    - language: "cn" -> answer in Chinese; otherwise English
    - model: "r1" uses setting.r1_model_name; anything else uses setting.v3_model_name
    """
    # Switch default model globally here if needed
    if language == "cn":
        sys = "You are a Chinese assistant; answer the user's question in Chinese."
    else:
        sys = "You are an English assistant; answer the user's question in English."

    if history is None:
        history = []

    if model == "r1":
        model = setting.r1_model_name
    else:
        model = setting.v3_model_name

    messages = history
    messages.append({"role": "user", "content": f"{sys}\n{_query}"})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=0.3,
    )

    reasoning_content = ""
    content = ""

    for chunk in response:
        # Be defensive: delta can be None on some keep-alive chunks
        delta = getattr(chunk.choices[0], "delta", None)
        if not delta:
            continue

        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            reasoning_content += delta.reasoning_content
            print(delta.reasoning_content, end="")
        elif hasattr(delta, "content") and delta.content:
            content += delta.content
            print(delta.content, end="")

    return content


if __name__ == "__main__":
    pass

# ------------------------------------------------------------------
# Example prompts (commented out). Translated to English for reference
# ------------------------------------------------------------------

# query = """
# You are a medic in Delta Force (an FPS game). You and your squad are on a mission:
# keep teammates safe and help them fill their backpacks with high-value loot.
#
# <Situation>
# Teammate HP 10/100
# Enemy headcount high; we are at a disadvantage
# </Situation>
#
# <Skills>
# [Hormone Gun]: restores teammate HP   status 6/6 (available)
# [Smoke Grenade]: deploy smoke cover   status cooling down
# </Skills>
#
# Teammate voice command:
# <Command>
# "Go check upstairs for enemy count, be careful."
# </Command>
#
# You must:
# 1) Decide the immediate action to take
# 2) Reply verbally to the teammate
# 3) Style: colloquial, brief, human-like, slightly vague, ≤10 characters
#
# Allowed actions:
# prone, crouch, attack, retreat, scout, stop attack, find cover, smoke, follow human,
# heal human, heal self, share supplies, rescue teammate, stop looting, other intent
#
# Output JSON only. Example:
# {"intent":"follow human","reply":"let’s move"}
# """
#
# ppt = load_json("carrier_4g_flow_analysis_flat.json")
# prompt = f"""
# Based on the PPT content below, generate an outline for a carrier 4G traffic analysis
# report (JSON). The outline will serve as a prompt to guide metric analysis and
# explain IoT status and challenges.
#
# {{PPT CONTENT}}
#
# Requirements:
# - Each section: title, brief description (can be empty), "principle" (writing rules),
#   and "info_needed" (metrics to use).
# - Titles concise; cover all aspects of 4G traffic analysis.
# - "principle" must clearly describe style and focus.
# Output JSON array like:
# [
#   {"title":"...","level":"...","content":"","principle":"...","info_needed":"..."},
#   ...
# ]
# """
# prompt = prompt.replace("{PPT CONTENT}", str(ppt))
# ans = ask_deepseek(prompt, model="r1")
# ans = ans.replace("```", "").replace("json", "").strip()
# print(ans)
# ans = json.loads(ans)
#
# content = """
# I need to check whether "planning execution progress" is included.
# If not mentioned, prompt for supplementation. I’ll scan each page summary for
# signals of execution progress.
#
# page1: "2024 plan execution: completed phase-6 5G rollout, improved coverage
# and split ratio; key scenarios & high-speed rail lines at high quality." -> yes.
#
# page2: province overview, policy & planning—no execution progress -> no.
#
# page3: current 4G network distribution, site counts, indoor coverage—no execution progress -> no.
#
# page4: 5G station scale and deployment status; progress ‘smooth’. Ambiguous; not clearly
# labeled as plan execution progress. To be safe, only page1 qualifies.
# """
#
# test_prompt1 = f"""
# <Task>Write a ≤50-character summary of the CONTENT</Task>
# <Requirements>
# 1) First-person phrasing
# 2) "Thought → Action" format
# </Requirements>
# <CONTENT>
# {content}
# </CONTENT>
# <Output Example>
# Thought: I need to confirm whether planning execution progress is present.
# Action: Only page1 explicitly mentions it; others don’t. Select page1 and
# suggest adding progress details elsewhere.
# </Output Example>
# """
#
# test_prompt2 = """
# You are a consulting expert. Based on the checklist item, find the 3–5 PPT pages
# that most need review. Output JSON: {"output":"page1;;page2;;page3"}.
# <ppt>{ppt}</ppt>
# <checklist> Check completeness of province basic information </checklist>
# Please output JSON.
# """
#
# messages = [
#     {"role": "user", "content": "Please check whether this file meets the review criteria."},
#     {"role": "assistant", "content": "After inspection, the file meets the requirements."},
#     {"role": "user", "content": "What’s the weather like in Chengdu, Sichuan?"},
#     {"role": "assistant", "content": "Sorry, I can’t access the Internet and don’t know the weather."}
# ]
#
# # Simple intent classifier loop (chat / Q&A / file review)
# messages = []
# while True:
#     print("\n")
#     query = input("Enter query: ")
#     ans = ask_deepseek(
#         "You are a consulting advisor. Use conversation history + the current "
#         "message to infer the user’s true intent. The only options are: [chat, "
#         "question, file_review]. Output exactly one label.\n"
#         "Examples:\n"
#         "Input: hello  -> chat\n"
#         "Input: who are you -> chat\n"
#         "Input: What’s the weather in Chengdu, Sichuan? -> chat\n"
#         "Input: What are fun places in Beijing? -> question\n"
#         "Input: Please review whether this document meets requirements -> file_review\n"
#         f"Current message: {query}",
#         model="v3",
#         history=messages,
#     )
#
#     labels = ["chat", "question", "file_review"]
#
#     import difflib
#
#     def find_most_similar(target, candidates) -> str:
#         """Find the candidate string most similar to target."""
#         if not candidates:
#             return None
#         scores = [(c, difflib.SequenceMatcher(None, target, c).ratio()) for c in candidates]
#         return max(scores, key=lambda x: x[1])[0]
#
#     ans = find_most_similar(ans.strip(), labels)
#     print("Final intent:", ans)
#
#     if ans != "chat":
#         mainland_provinces = [
#             "Beijing", "Tianjin", "Shanghai", "Chongqing",
#             "Hebei", "Shanxi", "Liaoning", "Jilin", "Heilongjiang",
#             "Jiangsu", "Zhejiang", "Anhui", "Fujian", "Jiangxi", "Shandong",
#             "Henan", "Hubei", "Hunan", "Guangdong", "Hainan",
#             "Sichuan", "Guizhou", "Yunnan", "Shaanxi", "Gansu", "Qinghai",
#             "Inner Mongolia", "Guangxi", "Tibet", "Ningxia", "Xinjiang", "None"
#         ]
#         location = ask_deepseek(
#             "Extract the province name from the user’s message. "
#             f"User message: {query}\n"
#             f"Output only the province name or 'None'. Valid options: {mainland_provinces}",
#             history=messages,
#             model="v3",
#         )
#         location = find_most_similar((location or "").strip(), mainland_provinces)
#         if location == "None":
#             print("Please provide the relevant province.")
#
#     if ans == "chat":
#         reply = ask_deepseek(query, model="v3", history=messages)
#     elif ans == "question":
#         reply = "Triggered document Q&A; result obtained."
#         print("\nStarting document Q&A…")
#     else:
#         reply = "Triggered document review; result obtained."
#         print("\nStarting document review…")
#
#     messages.append({"role": "user", "content": query})
#     messages.append({"role": "assistant", "content": reply})
#     if len(messages) >= 16:
#         messages = messages[-16:]
