# -*- coding:utf-8 -*-
from views import util

__author__ = 'AE'
import sys

reload(sys)
sys.setdefaultencoding("utf8")
from views.index import BaseHandler
from views.util import dictMerge
from settings import settings as config


class CategoryList(BaseHandler):
    """
    根据tag的id查询
    """
    def get(self, *args, **kwargs):
        id = args[0]
        pN = args[1]
        sqlPre = config.queryAll \
              + config.queryWhereByCategoryID \
              + config.queryGroupByArticleId \
              + config.queryOrderBydateAndId \
              + config.queryByLimit
        # 获取分页结果和页码、总页数
        result,pageNum,totalPages = util.getPage(self.application.conn.cursor(),
                                                 sqlPre,
                                                 pN,
                                                 id)

        self.render("index.html", articleList=result,startPage=pageNum+1,totalPages = totalPages)
