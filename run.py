#-*- coding:utf-8 -*-
import sys
from tornado_mysql import pools,cursors

reload(sys)
sys.setdefaultencoding("utf8")
from views.article import ArticleDetail, DateList, AddArticle, ModifyArticle, ArticlePage, DelArticle
from views.category import CategoryList
from views.image import ImageUpload
from views.tag import TagList
from views.index import *
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
from tornado.options import define,options
from settings import settings as config
import pymysql

# 使用命令行配置数据库参数，或者使用setting的配置文件
#python run.py --port=8000 --mysqlhost=192.168.56.1 --mysqlport=3306 --mysqldatabase=blog_tornado --mysqluser=root --mysqlpassword=0000
define("port",default=config.WEB_PORT,help="run on the given port",type = int)
# 数据库配置
define("mysqlhost", default=config.DATABASES.get("host"),help="database host",type=str)
define("mysqlport", default=config.DATABASES.get("port"), help="database port",type = int)
define("mysqldatabase", default=config.DATABASES.get("database"), help="database name",type=str)
define("mysqluser", default=config.DATABASES.get("user"),help="database user",type=str)
define("mysqlpassword",default=config.DATABASES.get("password"), help="database password",type=str)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            tornado.web.URLSpec(r"/",Index,name="/"),
            tornado.web.URLSpec(r"/(\d*)",ArticlePage,name="index"),
            tornado.web.URLSpec(r"/login",Login,name="login"),
            tornado.web.URLSpec(r"/logout",Logout,name="logout"),
            tornado.web.URLSpec(r"/article/detail/(\d+)",ArticleDetail,name="articleDetail"),
            tornado.web.URLSpec(r"/article/tag/(\d+)/(\d*)",TagList,name="articleTag"),
            tornado.web.URLSpec(r"/article/category/(\d+)/(\d*)",CategoryList,name="articleCategory"),
            tornado.web.URLSpec(r"/article/date/(\d{4}-\d{2}-\d{2})/(\d*)",DateList,name="articleDate"),
            tornado.web.URLSpec(r"/article/add",AddArticle,name="addArticle"),
            tornado.web.URLSpec(r"/imageupload",ImageUpload,name="imageupload"),
            tornado.web.URLSpec(r"/article/modify/(\d+)",ModifyArticle,name="ModifyArticle"),
            tornado.web.URLSpec(r"/article/delete/(\d+)",DelArticle,name="DelArticle"),
        ]
        settings = config.settings
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers
        self.conn = pymysql.connect(
            host=options.mysqlhost,
            port=options.mysqlport,
            user=options.mysqluser,
            passwd=options.mysqlpassword,
            db=options.mysqldatabase,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())

    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

