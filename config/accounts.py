# -*- coding: utf-8 -*-
"""
推特博主配置 - 影响美股/A股的关键人物清单
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TwitterAccount:
    """推特账号信息"""
    username: str  # 推特用户名（不含@）
    name: str  # 人物/机构名称
    category: str  # 分类
    influence_scope: List[str]  # 影响标的
    watch_for: List[str]  # 关注内容
    characteristics: str  # 特点
    priority: int  # 优先级（1-5，1最高）
    enabled: bool = True  # 是否启用


# ============================================
# 一、一句话能炸盘的顶级人物
# ============================================

TIER_1_INFLUENCERS = [
    TwitterAccount(
        username="elonmusk",
        name="埃隆·马斯克",
        category="顶级人物",
        influence_scope=["TSLA", "美股科技/AI", "加密货币", "电动车产业链"],
        watch_for=[
            "对特斯拉产能、销量、AI、自动驾驶的表态",
            "突然点名某家公司/概念",
            "对美联储、利率、经济的吐槽"
        ],
        characteristics="短线波动极强，经常日内反转",
        priority=1
    ),
    TwitterAccount(
        username="realDonaldTrump",
        name="特朗普",
        category="顶级人物",
        influence_scope=["道琼斯", "大盘指数", "关税相关（制造业、零售、钢铁、汽车）", "能源", "军工"],
        watch_for=[
            "关税、贸易战言论",
            "对美联储、加息的批评",
            "对特定公司/行业点名"
        ],
        characteristics="直接影响市场风险偏好，大盘应声动",
        priority=1
    ),
    TwitterAccount(
        username="CathieWood",
        name="凯西·伍德（ARK基金）",
        category="顶级人物",
        influence_scope=["ARKK/ARKW/ARKF等ETF", "特斯拉", "Coinbase", "AI/机器人/创新科技股"],
        watch_for=[
            "加仓/减仓预告、目标价、行业判断",
            "对美联储、通缩/通胀的观点"
        ],
        characteristics="成长股风向标，散户跟随度极高",
        priority=2
    ),
    TwitterAccount(
        username="BillAckman",
        name="比尔·阿克曼（对冲基金大佬）",
        category="顶级人物",
        influence_scope=["银行股", "债券", "利率", "大盘情绪"],
        watch_for=[
            "对美联储加息/降息的喊话",
            "做空/做多某类资产表态"
        ],
        characteristics="机构认可度高，一句话影响债市→传导股市",
        priority=2
    ),
    TwitterAccount(
        username="Carl_C_Icahn",
        name="卡尔·伊坎（激进投资大佬）",
        category="顶级人物",
        influence_scope=["被他盯上的个股", "传统行业", "消费", "能源"],
        watch_for=[
            "宣布入股某公司、要求管理层改革"
        ],
        characteristics="被点名个股经常暴涨暴跌",
        priority=2
    ),
]

# ============================================
# 二、决定美股"生死线"的官方账号
# ============================================

OFFICIAL_ACCOUNTS = [
    TwitterAccount(
        username="federalreserve",
        name="美联储",
        category="官方机构",
        influence_scope=["全美股", "银行股", "成长/价值风格切换"],
        watch_for=[
            "利率决议、会议纪要、官员讲话原文",
            "通胀、就业、经济展望"
        ],
        characteristics="所有波动的根源，必须盯",
        priority=1
    ),
    TwitterAccount(
        username="SECGov",
        name="美国SEC",
        category="官方机构",
        influence_scope=["加密货币", "科技巨头", "中概股", "SPAC", "IPO"],
        watch_for=[
            "监管新规、起诉公告、ETF审批动态"
        ],
        characteristics="利空一出，相关板块直接跳水",
        priority=1
    ),
    TwitterAccount(
        username="USTreasury",
        name="美国财政部",
        category="官方机构",
        influence_scope=["美元", "债券", "银行体系", "市场流动性"],
        watch_for=[
            "发债计划、救市/稳定市场表态"
        ],
        characteristics="影响全球流动性预期",
        priority=2
    ),
]

# ============================================
# 三、短线交易神器
# ============================================

TRADING_TOOLS = [
    TwitterAccount(
        username="Unusual_Whales",
        name="Unusual Whales",
        category="交易工具",
        influence_scope=["全市场个股"],
        watch_for=[
            "大额看涨/看跌期权扫单",
            "财报前、事件前的提前异动"
        ],
        characteristics="经常提前预示暴涨暴跌",
        priority=2
    ),
    TwitterAccount(
        username="MarketChameleon",
        name="Market Chameleon",
        category="交易工具",
        influence_scope=["期权数据", "成交量异动"],
        watch_for=[
            "期权数据、成交量异动"
        ],
        characteristics="适合短线、抓财报行情",
        priority=3
    ),
    TwitterAccount(
        username="Stocktwits",
        name="Stocktwits",
        category="交易工具",
        influence_scope=["美股散户情绪"],
        watch_for=[
            "热门股热度、逼空情绪、恐慌/狂热指标"
        ],
        characteristics="美股散户情绪总龙头",
        priority=3
    ),
]

# ============================================
# 四、财经媒体 & 即时新闻
# ============================================

NEWS_MEDIA = [
    TwitterAccount(
        username="CNBC",
        name="CNBC",
        category="财经媒体",
        influence_scope=["全市场"],
        watch_for=[
            "突发新闻最快，财报、裁员、并购、经济数据"
        ],
        characteristics="做日内、做消息盘必看",
        priority=2
    ),
    TwitterAccount(
        username="WSJ",
        name="华尔街日报",
        category="财经媒体",
        influence_scope=["全市场"],
        watch_for=[
            "独家政策/并购新闻"
        ],
        characteristics="消息可信度最高",
        priority=2
    ),
    TwitterAccount(
        username="markets",
        name="Bloomberg Markets",
        category="财经媒体",
        influence_scope=["全球宏观", "汇率", "大宗商品"],
        watch_for=[
            "全球宏观、汇率、大宗商品联动美股"
        ],
        characteristics="全球宏观视角",
        priority=2
    ),
]

# ============================================
# 五、宏观大神
# ============================================

MACRO_ANALYSTS = [
    TwitterAccount(
        username="LynAldenContact",
        name="Lyn Alden",
        category="宏观分析师",
        influence_scope=["利率", "通胀", "美元"],
        watch_for=[
            "对利率、通胀、美元的观点"
        ],
        characteristics="宏观分析师，观点清晰",
        priority=3
    ),
    TwitterAccount(
        username="PeterSchiff",
        name="Peter Schiff",
        category="宏观分析师",
        influence_scope=["黄金", "美元", "通胀"],
        watch_for=[
            "黄金、美元、通胀观点"
        ],
        characteristics="黄金、美元、通胀老派大佬",
        priority=3
    ),
    TwitterAccount(
        username="zerohedge",
        name="ZeroHedge",
        category="宏观分析师",
        influence_scope=["风险预警"],
        watch_for=[
            "市场风险预警"
        ],
        characteristics="偏空头、风险预警，市场恐慌时传播极强",
        priority=3
    ),
]

# ============================================
# 六、极简关注清单（核心10个）
# ============================================

ESSENTIAL_ACCOUNTS = [
    "elonmusk",
    "realDonaldTrump",
    "CathieWood",
    "federalreserve",
    "SECGov",
    "BillAckman",
    "Unusual_Whales",
    "CNBC",
    "markets",
    "Stocktwits",
]

# 所有账号汇总
ALL_ACCOUNTS = (
    TIER_1_INFLUENCERS +
    OFFICIAL_ACCOUNTS +
    TRADING_TOOLS +
    NEWS_MEDIA +
    MACRO_ANALYSTS
)

# 按优先级排序
ALL_ACCOUNTS_SORTED = sorted(ALL_ACCOUNTS, key=lambda x: x.priority)


def get_enabled_accounts() -> List[TwitterAccount]:
    """获取所有启用的账号"""
    return [acc for acc in ALL_ACCOUNTS_SORTED if acc.enabled]


def get_essential_accounts() -> List[TwitterAccount]:
    """获取核心账号"""
    return [acc for acc in ALL_ACCOUNTS if acc.username in ESSENTIAL_ACCOUNTS and acc.enabled]


def get_account_by_username(username: str) -> Optional[TwitterAccount]:
    """根据用户名获取账号信息"""
    for acc in ALL_ACCOUNTS:
        if acc.username.lower() == username.lower():
            return acc
    return None
