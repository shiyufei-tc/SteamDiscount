import requests
import uvicorn
from lxml import html
import csv
import os
import Data_analyze
import logging
from fastapi import FastAPI,Request,status
from starlette.responses import FileResponse,JSONResponse

serve=FastAPI(title="discount")

@serve.exception_handler(Exception)
def handler_exception(request:Request,exc:Exception):
    logging.error(f"处理异常，请求路径{request.url},异常信息{exc}")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code":500,"message":"服务器内部错误","data":None})

@serve.get("/")
def root():
    return FileResponse("data/Games.csv")

DISCOUNT_URL_50="https://store.steampowered.com/search/?hwtype=0&supportedlang=schinese&specials=1&ndl=1"
DISCOUNT_URL_50M="https://store.steampowered.com/search/results/?query=&start={}&count=50&dynamic_data=&sort_by=_ASC&hwtype=0&supportedlang=schinese&snr=1_7_7_2300_7&specials=1&infinite=1"

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(levelname)s - "
        "[%(name)s:%(filename)s:%(lineno)d] - %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_response(discount_url: str) -> str:
    """
        函数作用:向steam发送请求
        param discount_url:打折页面的链接
        return:返回响应页面的html源码,若返回的是json数据则提取results_html内容
    """
    response=requests.get(discount_url,timeout=10)
    logging.info(f"向{discount_url}发送请求")

    #50个游戏即第1页之后之后的响应html在json文件中，看响应体的json文件
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        result = response.json()
        return result.get("results_html", "")
    
    response.encoding='utf-8'
    return response.text

def get_text(node, xpath: str) -> str | None:
    """
        函数作用:封装xpath的解析定位操作
        param node:节点
        param xpath:数据路径
        return:返回提取到的文本内容,若未找到则返回None
    """
    elements = node.xpath(xpath)
    if not elements:
        return None
    return elements[0].text_content().strip()

#解析定位返回数据
def parse_html(html_text: str) -> list[dict[str, str | None]]:
    """
        函数作用:解析页面的HTML内容并提取游戏信息
        param html_text:页面html源码
        return:返回当前页面中所有游戏信息的列表，每个元素为字典
    """
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

def save_csv(all_games: list[dict[str, str | None]]):
    """
        函数作用:将抓取到的游戏数据保存为CSV文件
        param all_games:要写入CSV的游戏列表
    """
    if not os.path.exists("data"):
        os.mkdir("data")
    with open("data/Games.csv",'w',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['name','discount','original_price','final_price'])
        writer.writeheader()
        writer.writerows(all_games)

def main():
    """
        函数作用:从用户输入中获取游戏数量并执行抓取、保存和清洗流程
    """
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
        logging.info("没有data文件夹中或无法打开文件")
    else:
        Data_analyze.Data_cleaning(df)


if __name__=="__main__":
    uvicorn.run(serve,host="0.0.0.0",port=8000)
    main()