"""
定义一些函数，定位网页，爬取网页内容
主要函数：
page_find:用来登录网页并定位至特定的页面元素，返回driver,给page_scrapy函数调用
page_scrapy：用来爬取当前页面，返回patent list列表
patent_scrapy：用来爬取page_find确定好的页面所有专利信息，返回patent list列表
"""
# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from loguru import logger
from retrying import retry


def cal_time(func):
    """
    装饰器，可以用来计时
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        stop_time = time.time()

    return wrapper


@retry(stop_max_attempt_number=5)
def page_find(url, keyword, start_date=None, end_date=None):
    """
    输出driver，登录至特定的页面上，并定位至特定的页面元素
    :param url:
    :param keyword:
    :param start_date:
    :param end_date:
    :return:
    """
    driver_path = r'E:\python\chromedriver.exe'
    s = Service(driver_path)
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    driver = webdriver.Chrome(service=s, options=option)
    driver.get(url)
    script1 = 'document.querySelector("#datebox0").removeAttribute("readonly")'
    script2 = 'document.querySelector("#datebox1").removeAttribute("readonly")'
    # script1 = 'document.getElementById("datebox0").removeAttribute("readonly")'
    # script2 = 'document.getElementById("datebox1").removeAttribute("readonly")'
    driver.execute_script(script1)
    driver.execute_script(script2)
    if start_date:
        driver.find_element(By.XPATH, r'//*[@id="datebox0"]').send_keys(start_date)
    if end_date:
        driver.find_element(By.XPATH, r'//*[@id="datebox1"]').send_keys(end_date)
    Select(driver.find_element(By.CLASS_NAME, 'reopt')).select_by_value('SQR')
    driver.find_element(By.ID, 'txt_1_value1').send_keys(keyword)
    driver.find_element(By.CLASS_NAME, 'search').click()
    time.sleep(1)
    driver.find_element(By.XPATH, r'//*[@id="perPageDiv"]/ul/li[3]').click()
    return driver


@retry(stop_max_attempt_number=5)
def page_scrapy(driver):
    """
    该函数被用来提取当前页面的专利信息
    :param driver:
    :return: patent->list
    """
    tbody = driver.find_element(By.XPATH, '//*[@id="gridTable"]/div/div[2]/table/tbody')
    tbody_tr = tbody.find_elements(By.TAG_NAME, 'tr')
    patent = []
    for tr in tbody_tr:
        td = tr.find_elements(By.TAG_NAME, 'td')
        patent.append([item.text for item in td])
    return patent


@retry(stop_max_attempt_number=5)
def patent_scrapy(url, keyword, start_date=None, end_date=None):
    """
    根据某一查询条件，包括网址、关键词、申请日期、结束日期，查询专利数，并爬取所有数据结果。
    :param url:
    :param keyword:
    :param start_date:
    :param end_date:
    :return:
    """
    driver = page_find(url, keyword, start_date, end_date)
    patent = page_scrapy(driver=driver)
    for i in patent:
        logger.info(i)
    while True:
        try:
            driver.find_element(By.ID, 'PageNext').click()
            # time.sleep(2)
            p = page_scrapy(driver=driver)
            for i in p:
                logger.info(i)
            patent.extend(p)
        except NoSuchElementException as e:
            logger.info('爬虫结束')
            break
    logger.info(f'共爬取{len(patent)}条专利信息！')
    driver.quit()
    return patent


if __name__ == '__main__':
    url = r'https://epub.cnki.net/kns/advsearch?dbcode=SCPD'
    # keyword = '中国石油化工股份有限公司石油工程技术研究院'
    keyword = '中国石油化工股份有限公司石油物探技术研究院'
    with open('run.log', 'w+') as file:
        file.truncate(0)
    logger.add('run.log', encoding='utf-8')
    logger.info('开始爬取2006年（不含）以前的专利信息')
    # patent = patent_scrapy(url, keyword, end_date='2005-12-31')
    patent = patent_scrapy(url, keyword)
