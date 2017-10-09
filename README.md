# scrapy-selenium-PhantomJS
最近比较迷selenium，此项目用其抓取了淘宝的商品页，起始url为s.taobao.com/search?q=电吉他&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20170930&ie=utf8&bcoffset=16&ntoffset=16&p4ppushleft=1%2C48&s=0
做了两步尝试：
首先是获取100页搜索页中所有商品的图片链接，标题，商家，价格，交易量等信息，这个比较简单，过程可见taobao.py
第二步更进一步，模拟点击每个商品详情页去获取其中的评论，过程比较复杂，经尝试实际运行效率很低，并不可取，但是作为模拟浏览器去爬还是有很多地方可以学习的。
例如为phantomsjs添加user-agent，cookies、在不同的窗口之间进行切换等等，项目详情请参考taobaocrawl.py

话说此项目大部分是基于selenium，与scrapy并没有什么关系。。纯粹是因为scrapy用的比较习惯了~哈哈
