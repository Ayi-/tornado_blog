# -*- coding:utf-8 -*-
import pickle
import tornado.web
from views.util import md
__author__ = 'AE'
try:
    import Cookie  # py2
except ImportError:
    import http.cookies as Cookie  # py3


class ArticleList(tornado.web.UIModule):
    def render(self, articleList, show_comments=False):
        return self.render_string(
            "module/articlelist.html", articleList=articleList, show_comments=show_comments)


class GetFlashedMessages(tornado.web.UIModule):
    def get_cookie(self, name, default=None):
        """Gets the value of the cookie with the given name, else default."""
        if self.request.cookies is not None and name in self.request.cookies:
            return self.request.cookies[name].value
        return default

    def render(self, with_categories=False, category_filter=[]):
        flashes = self.get_cookie('flashes_cookies')
        if flashes:
            flashes = tornado.escape.url_unescape(flashes)
            try:
                flash_data = pickle.loads(flashes)
                flashes = flash_data
                if category_filter:
                    flashes = list(filter(lambda f: f[0] in category_filter, flashes))
                if not with_categories:
                    flashes = [x[1] for x in flashes]
            except:
                flashes = None
        return self.render_string(
            "flash.html", flashes=flashes)


class GetMarkdown(tornado.web.UIModule):
    def render(self, article):
        return md(article)