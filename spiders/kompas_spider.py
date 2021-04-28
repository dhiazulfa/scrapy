import scrapy
import html2text
import re

XPATH_LINK = "//div[@class='article__list__title']/h3[@class='article__title article__title--medium']/a/@href"
#XPATH_NEXT_LINK = "//a[@class='paging__link paging__link--next']/@href"
XPATH_TITLE = "//h1[@class='read__title']/text()"
XPATH_AUTHOR = "//div[@id='penulis']/a/text()"
XPATH_DATE = "//div[@class='read__time']/text()"
XPATH_LOCATION = "//div[@class='read__content']/div/p/strong/text()"
XPATH_ARTICLE = "//div[@class='read__content']/div/p/text()"

class KompasSpider(scrapy.Spider):
    """docstring for KompasSpider."""

    # nama scrapy
    name = "kompas"
    # url awal yang di eksekusi
    start_urls = ['https://news.kompas.com/search/all']

    def parse(self,response):
 
        links = response.xpath(XPATH_LINK).extract()

        # mengambil link article untuk diambil content serta judulnya
        for link in links:
            yield scrapy.Request(url=link+'?fullpage',callback=self.parse)

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
                'location':response.xpath(XPATH_LOCATION).extract_first().strip(),
                'author':response.xpath(XPATH_AUTHOR).extract_first().strip(),
            }
