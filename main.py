# -*- coding: utf-8 -*-
"""
推特财经言论分析器 - 主入口
用法:
    python main.py [--mock] [--proxy http://host:port] [--hours 24] [--max 30]
环境变量:
    MOONSHOT_API_KEY - Moonshot AI API Key（用于分析）
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.accounts import get_enabled_accounts, ALL_ACCOUNTS
from src.fetcher import create_fetcher
from src.analyzer import TweetAnalyzer
from src.reporter import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def build_account_info():
    """构建账号信息字典供分析使用"""
    return {
        acc.username: {
            "name": acc.name,
            "scope": acc.influence_scope,
            "category": acc.category,
        }
        for acc in ALL_ACCOUNTS
    }


def run(mock_mode: bool = False, proxy: str = None, hours: int = 24, max_per: int = 30):
    """执行完整分析流程"""
    logger.info("=" * 60)
    logger.info("推特财经言论分析器启动")
    logger.info(f"模式: {'模拟' if mock_mode else '真实抓取'}, 回溯: {hours}小时, 每账号最多: {max_per}条")
    logger.info("=" * 60)

    # 1. 获取账号列表
    accounts = get_enabled_accounts()
    usernames = [acc.username for acc in accounts]
    logger.info(f"共 {len(usernames)} 个账号待分析: {', '.join(usernames)}")

    # 2. 抓取推文
    fetcher = create_fetcher(use_mock=mock_mode, proxy=proxy)
    tweets_dict = fetcher.fetch_accounts(usernames, hours_back=hours, max_per_account=max_per)

    # 展平为列表
    all_tweets = []
    for uname, tweets in tweets_dict.items():
        for t in tweets:
            all_tweets.append({
                "id": t.id,
                "username": t.username,
                "display_name": t.display_name,
                "content": t.content,
                "created_at": t.created_at,
            })
    logger.info(f"共抓取 {len(all_tweets)} 条推文")

    # 保存原始数据（无论是否抓到推文都创建目录）
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    raw_path = os.path.join(data_dir, f"tweets_{today}.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)
    logger.info(f"原始数据已保存: {raw_path}")

    if not all_tweets:
        logger.warning("未抓取到任何推文，生成空报告")

    # 3. AI 分析
    analyzer = TweetAnalyzer()
    account_info = build_account_info()
    analyses = analyzer.analyze_batch(all_tweets, account_info)
    logger.info(f"分析完成，共 {len(analyses)} 条结果")

    # 4. 生成报告
    reporter = ReportGenerator(output_dir=os.path.join(os.path.dirname(__file__), "reports"))
    report_path = reporter.save_report(analyses, date_str=datetime.now().strftime("%Y-%m-%d"))
    logger.info(f"报告已保存: {report_path}")

    # 5. 输出摘要
    high = sum(1 for a in analyses if a.market_impact == "高")
    urgent = sum(1 for a in analyses if a.urgency == "紧急")
    a_direct = sum(1 for a in analyses if a.a_share_relevance == "直接")

    logger.info("=" * 60)
    logger.info("分析摘要")
    logger.info(f"  高影响: {high} 条")
    logger.info(f"  紧急: {urgent} 条")
    logger.info(f"  直接影响A股: {a_direct} 条")
    logger.info(f"  报告路径: {report_path}")
    logger.info("=" * 60)

    return report_path


def main():
    parser = argparse.ArgumentParser(description="推特财经言论分析器")
    parser.add_argument("--mock", action="store_true", help="使用模拟数据模式")
    parser.add_argument("--proxy", type=str, default=None, help="代理地址，如 http://127.0.0.1:7890")
    parser.add_argument("--hours", type=int, default=24, help="回溯小时数")
    parser.add_argument("--max", type=int, default=30, help="每账号最大推文数")
    args = parser.parse_args()

    run(mock_mode=args.mock, proxy=args.proxy, hours=args.hours, max_per=args.max)


if __name__ == "__main__":
    main()
