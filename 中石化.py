import time
from loguru import logger
import pandas as pd
from functions import patent_scrapy
import sys

if __name__ == '__main__':
    url = r'https://epub.cnki.net/kns/advsearch?dbcode=SCPD'
    # keyword = '中国石油化工股份有限公司石油工程技术研究院'
    keyword = '中国石油化工股份有限公司'
    log_name = sys.argv[0].split('.')[0]
    with open(f'{log_name}.log', 'w+') as file:
        file.truncate(0)
    logger.add('run.log', encoding='utf-8')
    '''
    (1)-2005/12/31
    (2)2006/1/1-2008/12/31
    '''
    logger.info('开始爬取2006年（不含）以前的专利信息')
    patent = patent_scrapy(url, keyword, end_date='2005-12-31')
    for i in range(1, 5):
        logger.info(f'开始爬取200{i + 5}年的专利信息！')
        p = patent_scrapy(url, keyword, start_date=f'200{i + 5}-01-01', end_date=f'200{i + 5}-12-31')
        patent.extend(p)
    for i in range(0, 10):
        logger.info(f'开始爬取201{i}年的专利信息！')
        p = patent_scrapy(url, keyword, start_date=f'201{i}-01-01', end_date=f'201{i}-05-31')
        patent.extend(p)
        p = patent_scrapy(url, keyword, start_date=f'201{i}-06-01', end_date=f'201{i}-12-31')
        patent.extend(p)
    for i in range(0, 3):
        logger.info(f'开始爬取202{i}年的专利信息！')
        p = patent_scrapy(url, keyword, start_date=f'202{i}-01-01', end_date=f'202{i}-05-31')
        patent.extend(p)
        p = patent_scrapy(url, keyword, start_date=f'202{i}-06-01', end_date=f'202{i}-12-31')
        patent.extend(p)

        logger.info(f'开始爬取2023年的专利信息！')
        p = patent_scrapy(url, keyword, start_date='2023-01-01')
        patent.extend(p)
    logger.info(f'爬取完成，共爬取{len(patent)}条专利！')
    patent = pd.DataFrame(patent, columns=['序号', '专利名称', '发明人', '申请人', '申请日', '公开日', '备注'])
    patent['发明人'] = patent['发明人'].apply(lambda x: ','.join(x.split(' ')))
    patent['申请人'] = patent['申请人'].apply(lambda x: ','.join(x.split(' ')))
    patent.to_excel('工程院专利发表情况.xlsx', index=False)
