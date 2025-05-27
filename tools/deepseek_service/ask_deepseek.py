from openai import OpenAI
import setting

client = OpenAI(
    # 从环境变量中读取您的方舟API Key
    api_key=setting.deepseek_api_key,
    base_url=setting.deepseek_api_url
)


def ask_deepseek(_query, model="v3", history=None):
    # 统一替换默认模型可以全局修改
    if history is None:
        history = []
    if model == "r1":
        model = setting.r1_model_name
    else:
        model = setting.v3_model_name
    messages = history
    messages.append({"role": "user", "content": f"{_query}"})
    response = client.chat.completions.create(model=model, messages=messages, stream=True)
    reasoning_content = ""
    content = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
            reasoning_content += chunk.choices[0].delta.reasoning_content
            # print(chunk.choices[0].delta.reasoning_content, end="")
        else:
            content += chunk.choices[0].delta.content
            # print(chunk.choices[0].delta.content, end="")
    return content


if __name__ == "__main__":
    query = """
    你是三角洲行动（一款FPS游戏）里的医疗兵，你正在和你的队友执行任务，目标是保证队友的安全，并帮助队友尽可能把背包装满高价值物资。
    当前游戏局势为
    <局势>
    队友血量 10/100
    敌方人数较多，我方劣势
    </局势>
    你目前已有技能为
    <技能列表>
    [激素枪]：帮助队友恢复血量 技能状态 6/6 可使用
    [烟雾弹]：释放烟雾掩护队友 技能状态 仍在冷却中
    </技能列表>
    
    现在，队友向你发出的语音指令为
    <指令>
    你去看看楼上有几个敌人，注意安全
    </指令>
    
    现在你需要
    1、识别当前应当采取的措施
    2、语言回复队友的话
    3、语言风格尽可能通俗，简短，模仿人类语言，含糊，不可以超过十个字
    
    要求：你采取的措施必须在以下范围内
    趴下、蹲下、进攻、撤退、侦察、停止进攻、寻找掩体、封烟、跟随真人、治疗真人、治疗自身、分享物资、救援队友、停止捡物资、其他意图
    
    要求：输出json文件，表达你的想法
    示例：
    {
    "intent":"跟随真人"，
    "replay":"我们走吧，这里没有物资了"
    }
    请只输出json
    """
    ask_deepseek(query, model="v3")
