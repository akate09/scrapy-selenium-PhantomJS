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
from selenium.webdriver import ActionChains
from cookies import cookies

#设置文本输出环境为utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class TaobaocrawlSpider(scrapy.Spider):
    name = "taobaocrawl"
    allowed_domains = ['s.taobao.com','item.taobao.com','detail.tmall.com']
    #起始页面为电吉他商品页的第一页
    start_urls = ['http://s.taobao.com/search?q=%E7%94%B5%E5%90%89%E4%BB%96&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20170930&ie=utf8&bcoffset=16&ntoffset=16&p4ppushleft=1%2C48&s=0']

    def __init__(self):
        scrapy.spiders.Spider.__init__(self)
        #定义phantomjs浏览器并设置浏览器头
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
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
        print response.url
        #这部分为浏览器添加cookie，cookie格式自行利用抓包工具取得
        self.driver.get(response.url)
        self.driver.delete_all_cookies()
        cookie_list = []
        for cookie in cookies.keys():
            cookie_list.append({'name':cookie,'value':cookies[cookie],'domain':'.taobao.com','path':'/'})
        time.sleep(2)
        #提醒：分两次访问，并删除第一次访问的cookie，添加登陆后的cookie
        self.driver.delete_all_cookies()
        for ck in cookie_list:
            self.driver.add_cookie(ck)
        self.driver.get(response.url)
        time.sleep(2)
        #self.driver.save_screenshot('login.png')

        while True:
            try:
                #等待商品项目栏加载完毕
                element = WebDriverWait(self.driver,30).until(EC.presence_of_all_elements_located((By.ID,'mainsrp-itemlist')))
                #等待下一页标签出现
                element2 = WebDriverWait(self.driver,30).until(EC.presence_of_all_elements_located((By.XPATH,'//li[@class="item next"]')))
            except Exception, e:
                print Exception, ":", e
                print "wait failed"
                #结束程序
                break

            #此时已经得到了页面的源代码，可以做提取分析
            html = etree.HTML(self.driver.page_source)
            #product_num = int(html.xpath('//div[@class="items"][1]/div[last()]/@data-index')[0])

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
                for string in each.xpath('.//div[@class="row row-2 title"]/a//text()'):
                    title += string
                item['title'] = title.replace(' ','').strip()

                #商品详情页点击,用于获取评论，根据每个超链接的id调用解析函数获取每个商品的评论数
                link_id = str(each.xpath('.//div[@class="row row-2 title"]/a/@id')[0])
                href = str(each.xpath('.//div[@class="row row-2 title"]/a/@href')[0])
                comments = self.parse_content(link_id,href)
                item['comment'] = comments
                
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
            #在用浏览器解析完商品详情页后要将浏览器切换回到原来的搜索页
            if html.xpath('//li[@class="item next"]'):
                times = 0
                #print self.driver.current_url
                while times <= 2:
                    try:
                        self.driver.find_element_by_xpath('//li[@class="item next"]/a').click()
                    except:
                        self.driver.save_screenshot('123456.png')
                        print '重试第%d次'%(times+1)
                        times += 1
                        if times == 3:
                            print '重试三次失败'
                            break
                    else:
                        break
            else:
                break

            
    def parse_content(self,link_id,href):
        #一般搜索首页开始几个商品是淘宝的直通车广告，网址是以click开头的，需要通过模拟点击标签来获取商品献详情页,且展示的商品是天猫的
        if re.search('click',href):
            #引入鼠标动作链模拟点击
            print self.driver.current_url
            try:
                element3 = WebDriverWait(self.driver,5).until(EC.presence_of_all_elements_located((By.ID,link_id)))
            except:
                self.driver.save_screenshot('gg.png')
                return '没有找到该商品'

            ac = self.driver.find_element_by_xpath('//a[@id="%s"]'%link_id)
            ActionChains(self.driver).move_to_element(ac).click(ac).perform()

            #注意：点击链接以后会新开一个页面，必要手动将浏览器切换到新页面！否则一直停留在搜索页
            current_window = self.driver.current_window_handle
            handles = self.driver.window_handles
            self.driver.switch_to_window(handles[-1])
            self.driver.maximize_window()

            print '已点击商品标题'
            #首先获取天猫商品页，经过截图可以发现店铺内容是异步加载的，要通过下拉滚动条加载评论页面
            try:
                element = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//ul[@class="tabbar tm-clear"]')))
            except:
                self.driver.save_screenshot('diantu.png')
                print '页面获取失败'
                self.driver.switch_to_window(current_window)
                return ''

            #如果没发生异常，执行下拉滚动条的js命令加载页面
            js="document.body.scrollTop=1000"
            self.driver.execute_script(js)
            time.sleep(2)

            #此处其实应该加入try！但是采用sleep的方式等待页面，后续可以完善
            ac2 = self.driver.find_element_by_xpath('//ul[@class="tabbar tm-clear"]/li[2]/a')
            ActionChains(self.driver).move_to_element(ac2).click(ac2).perform()
            print '已经点击商品评论页'

            try:
                element2 = WebDriverWait(self.driver,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'tm-rate-content')))
            except:
                print '评论获取失败'
                self.driver.switch_to_window(current_window)
                return ''

            #取得评论页面的源码
            html2 = etree.HTML(self.driver.page_source)
            print '已经获取评论页面'
            comment_list = []
            #检验变量
            count = 1
            while True:
                if not html2.xpath('//span[@class="rate-page-next"]'):
                    print '正在获取第%d页评论'%count
                    for each in html2.xpath('//div[@class="rate-grid"]//tr'):
                        comments = ''
                        for comment in each.xpath('.//div[@class="tm-rate-fulltxt"]/text()'):
                            comments += comment
                        print comments
                        comment_list.append(comments)

                    #点击下一页
                    try:
                        self.driver.find_element_by_xpath('//div[@class="rate-paginator"]/a[last()]').click()
                        time.sleep(1)
                    except:
                        self.driver.save_screenshot('comments.png')
                        print '第%d页评论获取失败'%count
                        self.driver.switch_to_window(current_window)
                        return comment_list

                    #等待新评论的加载
                    try:
                        element3 = WebDriverWait(self.driver,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'tm-rate-content')))
                    except:
                        print '22评论获取失败'
                        self.driver.switch_to_window(current_window)
                        return comment_list
                    count += 1
                    html2 = etree.HTML(self.driver.page_source)
                else:
                    print '正在获取last page'
                    for each in html2.xpath('//div[@class="rate-grid"]//tr'):
                        comments = ''
                        for comment in each.xpath('.//div[@class="tm-rate-fulltxt"]/text()'):
                            comments += comment
                        comment_list.append(comments)
                    print '所有评论已经获取完毕'
                    break
            #将浏览器切换回搜索页面
            self.driver.switch_to_window(current_window)
            return comment_list

        else:
            return '还没评论'








