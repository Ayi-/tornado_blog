#-*- coding:utf-8 -*-
import sys
from views.flash.flash import FlashHandler

reload(sys)
sys.setdefaultencoding("utf8")

from tornado.options import define,options
import tornado.web
from tornado import ioloop, gen
from views.util import dictMerge
from settings import settings as config

__author__ = 'AE'

class BaseHandler(tornado.web.RequestHandler,FlashHandler):
    # def get_current_user(self):
    #     return self.get_secure_cookie("user")
    # http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.current_user
    @gen.coroutine
    def prepare(self):
        self._flashes=None
        # 返回request后就清除了，本次request内依旧可用
        self.clear_cookie('flashes_cookies')
        user = self.get_secure_cookie("user")
        self.current_user =user
        # 获取连接
        self.application.conn.ping(True)

class Login(BaseHandler):
    """
    登陆
    """
    def get(self):

        if not self.current_user:
            username = self.get_argument('username',None)
            password = self.get_argument('password',None)
            if password not in(None,"") and password not in(None,""):

                with self.application.conn.cursor() as cursor:
                    cursor.execute("select username,email from user where username = %s and password = %s", (username,password))
                    result = cursor.fetchone()
                    print result

                    if result:
                        self.set_secure_cookie("user",result.get("username"))
                        print result.get("username")
                    self.redirect(self.get_argument("next","/"))
                    return
            else:
                self.flash(u"用户名或密码错误")
        else:
            self.flash(u"不要重复登陆！",'error')
        self.redirect("/")

class Logout(BaseHandler):
    """
    注销
    """
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        print self.request.uri
        self.redirect(self.get_argument("next","/"))
