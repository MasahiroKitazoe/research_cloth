# coding: utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json
from research_api.settings.base import BASE_DIR

from users.models import User

BASE_URL = "https://www.dressinn.com"


def scrape_popular_items(url):
  """
  引数のurlに掲載されている商品の情報をスクレイピングして返す関数
  """
  # 割引後値段を抜き出すための正規表現パターンをコンパイル
  ptn = re.compile(r'¥ \d+ ¥ (\d{1,6})$')

  executable_path = BASE_DIR + '/dress_inn/chromedriver'

  driver = webdriver.Chrome(executable_path=executable_path)
  driver.implicitly_wait(5)
  driver.get(url)
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  item_list = soup.find_all(class_="li_position_p")  # 商品情報が格納されているliタグを全て抜き出す

  results = {}

  for i in range(41):  # トップ40商品(10行分)の商品データを抜き出す
    try:
      item = item_list[i]
    except IndexError:
      break  # スクレイピング対象の商品がなくなったら、終了

    try:
      discount = item.find(class_="pestaniaDescuento").text
    except AttributeError:  #割引商品でない場合、スキップして次の商品へ
      continue

    try:
      price = item.find(class_="BoxPriceValor").text
      match = ptn.match(price)
      if match:
        price = match.group(1)

      name_tag = item.find(class_="BoxPriceName")
      name = name_tag.text

      tail_link = name_tag.find('a')['href']
      link = BASE_URL + tail_link

      size_tags = item.find_all(class_="cada_talla_qw")
      remain_sizes = []
      for size_tag in size_tags:
        remain_sizes.append(size_tag.text)
    except AttributeError:
      continue

    results[i+1] = {
                "商品名": name,
                "割引率": discount,
                "割引後値段": price,
                "在庫サイズ": remain_sizes,
                "商品詳細ページリンク": link
                }

  return json.dumps(results, ensure_ascii=False)


def auth_user(user_id, password):
  try:
    user = User.objects.filter(user_id=user_id, password=password)
    return True
  except User.DoesNotExist:
    raise ValueError("無効なユーザーです")
