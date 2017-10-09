# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from taobao.items import TaobaoItem
from scrapy.xlib.pydispatch import dispatcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy import signals
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
import re
import time

class TaobaocrawlSpider(scrapy.Spider):
    name = "taobaocrawl"
    allowed_domains = ['s.taobao.com','item.taobao.com','detail.tmall.com']
    #起始页面为电吉他商品页的第一页
    start_urls = ['http://s.taobao.com/search?q=%E7%94%B5%E5%90%89%E4%BB%96&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20170930&ie=utf8&bcoffset=16&ntoffset=16&p4ppushleft=1%2C48&s=0']

    def __init__(self):
        scrapy.spiders.Spider.__init__(self)
        #定义phantomjs浏览器

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                )
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver.set_page_load_timeout(20)
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(2000,2000)
        #设置分离器让爬虫退出的时候关闭浏览器
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.quit()

    def parse(self, response):

        #取得页面
        self.driver.get(response.url)
        while True:
            try:
                #等待商品项目栏加载完毕
                element = WebDriverWait(self.driver,30).until(EC.presence_of_all_elements_located((By.ID,'mainsrp-itemlist')))
                #等待下一页标签出现
                element2 = WebDriverWait(self.driver,30).until(EC.presence_of_all_elements_located((By.XPATH,'//li[@class="item next"]')))

                print 'element:\n', element
            except Exception, e:
                print Exception, ":", e
                print "wait failed"
                #结束程序
                break

            #此时已经得到了页面的源代码，可以做提取分析
            #print self.driver.page_source
            html = etree.HTML(self.driver.page_source)

            #注意：淘宝的商品items类分两类，一类是auction性质的，一类是personalityData性质的，其中personalityData仅第一页有，数据量比较有限，就不单独提取了。
            for each in html.xpath('//div[@class="items"][1]/div[@data-category="auctions"]'):
                item = TaobaoItem()
                #价格提取
                item['price'] = each.xpath('.//div[@class="price g_price g_price-highlight"]/strong/text()')[0]
                #交易量提取：格式为XX人付款，用正则表达式将其中的XX数量提取出来
                deal = each.xpath('.//div[@class="deal-cnt"]/text()')[0]
                deal_count = re.search('(\d+).*?',deal).group(1)
                item['deal'] = deal_count
                #标题提取
                title = ''
                for str in each.xpath('.//div[@class="row row-2 title"]/a//text()'):
                    title += str
                item['title'] = title.replace(' ','').strip()
                #图片链接提取
                try:
                    item['image_url'] = each.xpath('.//div[@class="pic"]/a/img/@src')[0]
                except:
                    item['image_url'] = ''
                #商店名称
                item['shop_name'] = each.xpath('.//div[@class="shop"]/a/span[2]/text()')[0]
                #商店位置
                item['place'] = each.xpath('.//div[@class="location"]/text()')[0]
                yield item

            #如果网页还有下一页标签可以点击，那么就继续发送请求
            #注意：直接访问提取的链接是不行的，淘宝给出的href是#，无法访问
            #如果加入重试循环这一方法应该也是可行的，详细的可以自己尝试……
            '''
            if html.xpath('//li[@class="item next"]'):
                href = html.xpath('//li[@class="item next"]/a/@href')[0]
                yield scrapy.Request(href,callback = self.parse)
            '''
            #采用模拟点击的方式获取下一页的信息。
            #注意，如果不加入重试变量经常会在运行中碰到‘element-is-no-longer-attached-to-the-dom-staleelementreferenceexception’这个错误，经查是因为ajax没有完全加载完毕，href链接地址没有加载完毕，加入重试循环以后这个问题就没了。
            if html.xpath('//li[@class="item next"]'):
                times = 0
                #print self.driver.current_url
                while times <= 2:
                    try:
                        self.driver.find_element_by_xpath('//li[@class="item next"]/a').click()
                    except:
                        time.sleep(1)
                        print '重试第%d次'%(times+1)
                        times += 1
                        if times == 3:
                            print '重试三次失败'
                            break
                    else:
                        break
            else:
                break

            



