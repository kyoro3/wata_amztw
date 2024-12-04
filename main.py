import requests
from bs4 import BeautifulSoup
import tweepy
import time
import re
import json
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# 現在のディレクトリをスクリプトのディレクトリに変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 商品情報を読み込む
with open('target.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

# Client を使用した認証
client = tweepy.Client(
    consumer_key=os.getenv("CONSUMER_KEY"),
    consumer_secret=os.getenv("CONSUMER_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

def check_stock_with_regex(target):
    target_url = "https://www.amazon.co.jp/dp/" + target['target_asin']

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # 在庫切れを示すテキストの正規表現
    out_of_stock_pattern = re.compile(r"在庫切れ|一時的に品切れ")

    # "カートに入れる" ボタンと在庫切れを示すテキストを両方チェック
    cart_button = soup.find(id="add-to-cart-button")
    out_of_stock_text = soup.find(string=out_of_stock_pattern)

    if cart_button and not out_of_stock_text:
        return True
    else:
        return False

def tweet(target):
    response = client.create_tweet(
        text=target['tweet_content'].format(product_name=target['product_name'])
    )

if __name__ == "__main__":
    # 在庫が確認された商品を管理するセット
    tweeted_products = set()

    while True:
        try:
            for target in targets:
                product_name = target['product_name']
                # すでにツイートした商品はスキップ
                if product_name in tweeted_products:
                    print(f"{product_name}:スキップ")
                    continue

                if check_stock_with_regex(target):
                    tweet(target)
                    print(f"{product_name}:ツイート完了")
                    tweeted_products.add(product_name)
                else:
                    print(f"{product_name}:在庫なし")
                time.sleep(10)
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        time.sleep(3600)  # 1時間ごとにチェック
