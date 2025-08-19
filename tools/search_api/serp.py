import http.client
import json
import setting

conn = http.client.HTTPSConnection("google.serper.dev")

headers = {
    'X-API-KEY': setting.serp_key,
    'Content-Type': 'application/json'
}


def search_google(query, language="cn"):
    # To enable actual searching, comment out the next line
    # return {}
    """
    :param query: search query string
    :param language: "cn" -> zh-cn, otherwise "en"
    :return: a result dictionary; the "organic" field contains organic results.
             If an "answerBox" field appears, you may treat it as the default answer.
    """
    if language == "cn":
        language = "zh-cn"
    else:
        language = "en"

    payload = json.dumps({
        "q": query,
        "gl": "cn",   # search country
        "hl": language  # language
    })
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    search_result = data.decode("utf-8")
    return json.loads(search_result)


"""
Reference output format
{
    "searchParameters": {
        "q": "Shanghai NEV (new energy vehicle) subsidy policy",
        "gl": "cn",
        "hl": "zh-cn",
        "type": "search",
        "engine": "google"
    },
    "answerBox": {
        "snippet": "Shanghai’s latest NEV subsidy policy includes: 1) From Jan 1, 2023, a CNY 10,000 purchase subsidy for pure electric vehicles. 2) Up to CNY 20,000 trade-in subsidy for eligible old-to-new transactions. 3) Certain purchase subsidies for NEVs in public/commercial sectors.",
        "snippetHighlighted": [
            "From Jan 1, 2023, a CNY 10,000 purchase subsidy for pure electric vehicles"
        ],
        "title": "Shanghai NEV Subsidy 2023 – AutoHome",
        "link": "https://www.autohome.com.cn/ask/3063704.html"
    },
    "organic": [
        {
            "title": "Shanghai NEV subsidy policy 2024 (latest)",
            "link": "https://m.sh.bendibao.com/zffw/285708.html",
            "snippet": "Shanghai announced a new CNY 10,000 subsidy for NEV trade-ins. Individual buyers of pure electric passenger cars ...",
            "date": "Apr 23, 2024",
            "position": 1
        },
        {
            "title": "[Policy] Guide to NEV trade-in subsidies (2024)",
            "link": "https://fgw.sh.gov.cn/fgw_zcjd/20240419/9f9bf09d331a4a0983ea4e58cb47edb4.html",
            "snippet": "1) Old vehicle: the scrapped or transferred vehicle must have been registered under the applicant by Dec 31, 2023. · 2) New vehicle · 3) Application process.",
            "date": "Apr 19, 2024",
            "position": 2
        },
        {
            "title": "[PDF] Shanghai measures to encourage purchase/use of NEVs",
            "link": "https://www.shanghai.gov.cn/cmsres/8b/8b7142fb55a54e8e9c133fec1d8d77e6/bf58ea803d29f2c40c4520d518d07135.pdf",
            "snippet": "For eligible pure electric vehicles, a municipal subsidy of 0.5× the central subsidy; for eligible PHEVs (including range-extended) with engine ≤1.6L, a municipal subsidy of 0.3× the central subsidy ...",
            "position": 3
        },
        {
            "title": "Shanghai steps up support for auto trade-ins",
            "link": "https://www.gov.cn/lianbo/difang/202501/content_7001649.htm",
            "snippet": "CNY 20,000 subsidy for scrapping eligible old cars and purchasing a new NEV; CNY 15,000 for scrapping an eligible fuel car and purchasing ≤2.0L fuel car.",
            "date": "Jan 29, 2025",
            "position": 4
        },
        {
            "title": "Municipal Commerce Commission: 2025 Shanghai auto trade-in subsidy policy",
            "link": "https://sww.sh.gov.cn/zwgkgfqtzcwj/20250214/ee34beab96564fbe8b46f5f458ad9a35.html",
            "snippet": "From Jan 1, 2025 to Dec 31, 2025, individual consumers purchasing NEVs listed in the official catalogues are eligible ...",
            "date": "Feb 12, 2025",
            "position": 5
        },
        {
            "title": "[PDF] Interim measures to encourage NEV purchase/use in Shanghai",
            "link": "https://www.shanghai.gov.cn/cmsres/d7/d729634dc77c4bb38548b9a651d6680d/393cc68c7ba07f361c95a23c409a4855.pdf",
            "snippet": "To alleviate congestion, preferential access may be given to NEVs when traffic restrictions are implemented ...",
            "position": 6
        },
        {
            "title": "Shanghai expands auto trade-in subsidies to out-of-town plates",
            "link": "https://m.thepaper.cn/newsDetail_forward_30634305",
            "snippet": "On Apr 12, Shanghai announced expanded support for auto trade-ins, extending subsidy eligibility to vehicles with non-Shanghai plates ...",
            "date": "Apr 13, 2025",
            "position": 7
        },
        {
            "title": "Vehicle purchase tax preferences",
            "link": "https://shanghai.chinatax.gov.cn/hdjl/lygk/202401/t470267.html",
            "snippet": "NEVs eligible for vehicle purchase tax reductions include pure electric, plug-in hybrid (incl. range-extended), and fuel‐cell vehicles meeting technical requirements ...",
            "date": "Jan 22, 2024",
            "position": 8
        },
        {
            "title": "Shanghai: CNY 15,000 subsidy for individuals replacing with a new EV this year",
            "link": "https://web.shobserver.com/wx/detail.do?id=813874",
            "snippet": "From Nov 1, 2024 to Dec 31, 2024, individuals buying a new pure electric passenger car priced ≥ CNY 50,000 are eligible ...",
            "date": "Nov 1, 2024",
            "position": 9
        }
    ],
    "relatedSearches": [
        {"query": "Shanghai measures encouraging NEV purchase/use"},
        {"query": "NEV subsidy policy overview"},
        {"query": "Shanghai NEV subsidies"},
        {"query": "Shanghai NEV subsidies 2025"},
        {"query": "NEV subsidies 2025"},
        {"query": "Shanghai car subsidy"},
        {"query": "Shanghai NEV policy"},
        {"query": "NEV subsidy policy"}
    ],
    "credits": 1
}
"""
