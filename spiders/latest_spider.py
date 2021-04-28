import scrapy
import html2text
import re

XPATH_LINK      = "//h3[@class='media__title']/a/@href"
XPATH_DATE      =   "//div[@class='detail__date']/text()"
XPATH_TITLE     =   "//h1/text()"
XPATH_AUTHOR    =   "//div[@class='detail__author']/text()"
XPATH_ARTICLE   =   "//div[@class='detail__body-text itp_bodycontent']/p/text()"
XPATH_LOCATION  =   "//div[@class='detail__body-text itp_bodycontent']/strong/text()"
XPATH_NEXT_LINK =   "//a[text()='Next']/@href"

class LatestSpider(scrapy.Spider):
    # naama scrapy
    name = "news_name"
    # url awal yang di eksekusi
    start_urls = ['http://news.detik.com/indeks']

    def parse(self,response):
        # mengambil link menuju page selanjutnya
        next_page = response.xpath(XPATH_NEXT_LINK).extract_first()

        links = response.xpath(XPATH_LINK).extract()
        # jika ada page selanjutnya
        if next_page and next_page not in response.url:
            yield response.follow(url=next_page,callback=self.parse)

        # mengambil link article untuk diambil content serta judulnya
        for link in links:
            yield scrapy.Request(url=link,callback=self.parse)

        # Jika article kosong
        if len(response.xpath(XPATH_ARTICLE).extract())==0:
                print ("[x] Data Kosong!")

        # jika article tidak kosong
        else:
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_emphasis = True
            yield {
            'link':response.url,
            'article':h.handle(' '.join(map(str,response.xpath(XPATH_ARTICLE).extract()))).replace('\n',''),
            'date':response.xpath(XPATH_DATE).extract_first().strip(),
            'title':response.xpath(XPATH_TITLE).extract_first().strip(),
            'author':response.xpath(XPATH_AUTHOR).extract_first().strip(),
            'location':response.xpath(XPATH_LOCATION).extract_first().strip()
            }
