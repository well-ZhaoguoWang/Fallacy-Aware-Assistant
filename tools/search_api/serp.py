import http.client
import json
import setting

conn = http.client.HTTPSConnection("google.serper.dev")

headers = {
  'X-API-KEY': setting.serp_key,
  'Content-Type': 'application/json'
}


def search_google(query, language="cn"):
    # 要打开搜索，注释掉下面这行
    return {}
    """
    :param query:
    :param language:
    :return:返回查询结果字典， "organic"字段为原始查询内容，出现"answerBox"字段时，可以默认拿这个字段作为答案
    """
    if language == "cn":
        language = "zh-cn"
    else:
        language = "en"

    payload = json.dumps({
        "q": query,
        "gl": "cn", # 搜索国家
        "hl": language # 语言
    })
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    search_result = data.decode("utf-8")
    return json.loads(search_result)

"""
参考输出格式（）
{
    "searchParameters": {
        "q": "上海新能源汽车优惠政策",
        "gl": "cn",
        "hl": "zh-cn",
        "type": "search",
        "engine": "google"
    },
    "answerBox": {
        "snippet": "上海市目前最新出台的新能源汽车补贴政策主要有以下几点： 1. 从2023年1月1日起，对纯电动汽车给予1万元的购置补贴。 2. 对符合条件的旧换新交易给予最高2万元的车辆交易补贴。 3. 对公共及商业领域购买新能源汽车给予一定的购置补贴。",
        "snippetHighlighted": [
            "从2023年1月1日起，对纯电动汽车给予1万元的购置补贴"
        ],
        "title": "上海新能源车补贴2023年最新政策 - 汽车之家",
        "link": "https://www.autohome.com.cn/ask/3063704.html"
    },
    "organic": [
        {
            "title": "上海新能源车补贴2024年最新政策",
            "link": "https://m.sh.bendibao.com/zffw/285708.html",
            "snippet": "上海新一轮10000元新能源车置换补贴政策发布，个人用户购买纯电动小客车新车，注册使用性质为非营运，且在规定期限内报废或者转让(不含变更登记)本人名下 ...",
            "date": "2024年4月23日",
            "position": 1
        },
        {
            "title": "【文字】新能源汽车置换补贴申请指南（2024年）_政策解读",
            "link": "https://fgw.sh.gov.cn/fgw_zcjd/20240419/9f9bf09d331a4a0983ea4e58cb47edb4.html",
            "snippet": "1、旧车. 一是报废或者转让的旧车应当于2023年12月31日前（含当日）注册登记在个人用户本人名下。 · 2、新车 · 三、补贴申请.",
            "date": "2024年4月19日",
            "position": 2
        },
        {
            "title": "[PDF] 上海市鼓励购买和使用新能源汽车实施办法",
            "link": "https://www.shanghai.gov.cn/cmsres/8b/8b7142fb55a54e8e9c133fec1d8d77e6/bf58ea803d29f2c40c4520d518d07135.pdf",
            "snippet": "对符合条件的纯电动汽车，按照中央财政补助1∶0.5 给予. 本市财政补助；对符合条件的插电式混合动力（含增程式）乘用. 车，且发动机排量不大于1.6 升的，按照中央财政补助1∶0.3 ...",
            "position": 3
        },
        {
            "title": "上海加力支持汽车以旧换新_地方动态 - 中国政府网",
            "link": "https://www.gov.cn/lianbo/difang/202501/content_7001649.htm",
            "snippet": "对报废上述符合条件旧车并购买新能源乘用车的，补贴2万元；对报废上述符合条件燃油乘用车并购买2.0升及以下排量燃油乘用车的，补贴1.5万元。",
            "date": "2025年1月29日",
            "position": 4
        },
        {
            "title": "市商务委等五部门关于印发《2025年上海市汽车置换更新补贴政策 ...",
            "link": "https://sww.sh.gov.cn/zwgkgfqtzcwj/20250214/ee34beab96564fbe8b46f5f458ad9a35.html",
            "snippet": "自2025年1月1日（含当日，下同）至2025年12月31日，个人消费者购买纳入《道路机动车辆生产企业及产品公告》或国家其他相关车型目录的新能源小客车（包括纯电动 ...",
            "date": "2025年2月12日",
            "position": 5
        },
        {
            "title": "[PDF] 上海市鼓励购买和使用新能源汽车暂行办法",
            "link": "https://www.shanghai.gov.cn/cmsres/d7/d729634dc77c4bb38548b9a651d6680d/393cc68c7ba07f361c95a23c409a4855.pdf",
            "snippet": "本市为缓解交通拥堵，采取机动车限行措施时，应当对新能 源汽车给予优惠和通行便利。 新能源汽车生产厂商或进口新能源汽车生产厂商设立或授 权的销售公司（以下统称“新能源汽 ...",
            "position": 6
        },
        {
            "title": "上海汽车以旧换新补贴范围扩大至外牌，有何用意？如何发力？",
            "link": "https://m.thepaper.cn/newsDetail_forward_30634305",
            "snippet": "4月12日上午，上海市商务委发布消息称，将进一步加力支持汽车置换更新，补贴范围扩大至外牌旧车。早在今年1月，上海官宣加力支持汽车以旧换新相关政策，当时 ...",
            "date": "2025年4月13日",
            "position": 7
        },
        {
            "title": "车辆购置税优惠",
            "link": "https://shanghai.chinatax.gov.cn/hdjl/lygk/202401/t470267.html",
            "snippet": "享受车辆购置税减免政策的新能源汽车，是指符合新能源汽车产品技术要求的纯电动汽车、插电式混合动力(含增程式)汽车、燃料电池汽车。新能源汽车产品技术 ...",
            "date": "2024年1月22日",
            "position": 8
        },
        {
            "title": "上海：个人消费者年内置换纯电动汽车获1.5万元购车补贴 - 上观",
            "link": "https://web.shobserver.com/wx/detail.do?id=813874",
            "snippet": "自2024年11月1日(含当日，下同)至2024年12月31日，个人消费者购买5万元以上（含）（以《机动车销售统一发票》上载明的金额为准）纯电动小客车新车，注册使用性质 ...",
            "date": "2024年11月1日",
            "position": 9
        }
    ],
    "relatedSearches": [
        {
            "query": "上海市鼓励购买和使用新能源汽车实施办法"
        },
        {
            "query": "新能源汽车补贴政策汇总"
        },
        {
            "query": "上海新能源补贴"
        },
        {
            "query": "上海新能源补贴2025"
        },
        {
            "query": "新能源汽车补贴2025"
        },
        {
            "query": "上海购车补贴"
        },
        {
            "query": "上海新能源汽车 政策"
        },
        {
            "query": "新能源补贴政策"
        }
    ],
    "credits": 1
}
"""



