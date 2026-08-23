import requests
from lxml import html
import csv
import os
import Data_analyze

DISCOUNT_URL_50="https://store.steampowered.com/search/?hwtype=0&supportedlang=schinese&specials=1&ndl=1"
DISCOUNT_URL_50M="https://store.steampowered.com/search/results/?query=&start={}&count=50&dynamic_data=&sort_by=_ASC&hwtype=0&supportedlang=schinese&snr=1_7_7_2300_7&specials=1&infinite=1"

#发送请求
def get_response(discount_url):
    response=requests.get(discount_url,timeout=10)
    print(f"向{discount_url}发送请求")

    #50个游戏即第1页之后之后的响应html在json文件中，看响应体的json文件
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        result = response.json()
        return result.get("results_html", "")
    
    response.encoding='utf-8'
    return response.text

def get_text(node, xpath):
    elements = node.xpath(xpath)
    if not elements:
        return None
    return elements[0].text_content().strip()

#解析定位返回数据
def parse_html(html_text):
    Page_Games=[]
    doc=html.fromstring(html_text)
    Game_Blocks=doc.xpath('//a[contains(concat(" ", normalize-space(@class), " "), ''" search_result_row ")]')
    for game in Game_Blocks:
        Page_Games.append({
            "name": get_text(game,'.//span[contains(@class, "title")]'),
            "discount": get_text(game,'.//div[contains(@class, "discount_pct")]'),
            "original_price": get_text(game,'.//div[contains(@class, "discount_original_price")]'),
            "final_price": get_text(game,'.//div[contains(@class, "discount_final_price")]'),
        })
    return Page_Games

def save_csv(all_games):
    if not os.path.exists("data"):
        os.mkdir("data")
    with open("data/Games.csv",'w',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['name','discount','original_price','final_price'])
        writer.writeheader()
        writer.writerows(all_games)

def main():
    number_games=int(input())
    if number_games>50:
        numper_pages=number_games//50
    else:
        number_games=1
    All_games=[]
    for page_num in range(1,numper_pages+1):
        if page_num==1:
            html_text=get_response(DISCOUNT_URL_50)
        else:
            html_text=get_response(DISCOUNT_URL_50M.format(50*(page_num-1)))
        Page_Games=parse_html(html_text)
        All_games.extend(Page_Games)
    save_csv(All_games)
    df=Data_analyze.get_pandas()
    if df is None:
        print("没有data文件夹中或无法打开文件")
    else:
        Data_analyze.Data_cleaning(df)


if __name__=="__main__":
    main()