# -*- coding: utf-8 -*-

# Scrapy settings for douban250 project

BOT_NAME = 'taobao'

SPIDER_MODULES = ['taobao.spiders']
NEWSPIDER_MODULE = 'taobao.spiders'

# 设置下载延迟
DOWNLOAD_DELAY = 1
# 禁用COOKIE，防止被检测
COOKIES_ENABLED = False


# 处理请求头，模仿浏览器登陆
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
   'Cache-Control':'max-age=0'
}

#模仿不同浏览器登陆，通过下载中间件随机选取
UserAgents = [
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
    'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
    'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
    'Mozilla/5.0 (Linux; U; Android 4.0.3; zh-cn; M032 Build/IML74K) AppleWebKit/533.1 (KHTML, like Gecko)Version/4.0 MQQBrowser/4.1 Mobile Safari/533.1'   
        ]

DOWNLOADER_MIDDLEWARES = {
    'taobao.middlewares.UserAgent': 200,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
}

#设置管道文件
ITEM_PIPELINES = {
    #'taobao.pipelines.TaobaoPipeline': 200,
    'taobao.pipelines.TaobaoPipeline2': 300
}

