## Weibo Crawler
基于scrapy框架，借助微博对外开放的API来迭代式采集同IMDB、豆瓣电影相关的演员博文、博文下热评、热评用户的博文等。此外还支持电影相关微博超话、话题文章的爬取。

---



## Python脚本结构

+ crawler
 + logs
 + spider
	+ weibo_chaohua.py
	+ weibo_topic.py
 + items.py
 + middlewares.py
 + pipelines.py
 + settings.py
 + utils.py
+ create_table.py


## 程序说明
create_table.py用于在本地数据库内创建相应名称的数据表 

settings.py用于定义一些全局变量(包括试错次数、数据库地址、代理地址等)

pipelings.py用于定义写入数据库表的算法，比如从网页获取结构化数据之后如何按列填入数据表

middlewares.py用于定义中间代理的运行方式

items.py用于定义网页的结构化数据，方便网页json内容的中间存储处理

spider内文件(如weibo_topic.py)均是特定的网页内容爬取方法，里面定义了对给定网页api的迭代式访问策略以及josn数据的处理

logs文件夹用于写入调试日志

## 配置需求
python >= 3.8.1

scrapy >= 1.8.0

## 运行方式
本地配置好MySQL数据库，修改settings.py文件适配本地环境

运行爬虫: `scrapy crawl xxx`, 其中`xxx`为spider文件内定义的爬虫名称
