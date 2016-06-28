# -*- coding:utf-8 -*-
import sys
import math
import re
from tornado import gen
from views import util
from views.index import BaseHandler
from views.util import dictMerge, convertDate, getMDSummary
from settings import settings as config
from datetime import datetime, timedelta
import tornado.web

reload(sys)
sys.setdefaultencoding("utf8")
import pytz

__author__ = 'AE'


class ArticleDetail(BaseHandler):

    def get(self, slug):
        sql = config.queryAll.replace(".summary",".content") + config.queryWhereById + config.queryOrderBydateAndId
        with self.application.conn.cursor() as cursor:
            cursor.execute(sql, slug)
            result = dictMerge(cursor.fetchall(), "id")
        if (result):
            result = result[0]
        else:
            self.flash(u"该文章不存在！", "error")
            result = None
        # res[0]一篇文章就一个结果
        self.render("article.html", article=result, modifyFlag=True)


class ArticlePage(BaseHandler):


    def get(self, *args, **kwargs):
        pN = args[0]
        sqlPre = config.queryAll + config.queryGroupByArticleId + config.queryOrderBydateAndId + config.queryByLimit
        result, pageNum, totalPages = util.getPage(self.application.conn.cursor(),
                                                   sqlPre,
                                                   pN, )
        # with self.application.conn.cursor() as cursor:
        #     # 获取ID
        #     cursor.execute(sqlPre,(config.pageLimit,offset))
        #     result = cursor.fetchall()
        #     idList = [item['id'] for item in result ] # [49, 50, 48, 47, 46, 45, 44, 43, 37, 36]
        #     # 获取总数量
        #     cursor.execute(config.queryCount)
        #     totalPages = math.ceil((cursor.fetchone().values()[0])/config.pageLimit)
        #     if(len(idList)<1):
        #         result=None
        #     else:
        #         # 批量查询
        #         sql=config.queryAll+config.queryWhereInById % ', '.join(list(map(lambda x: '%s', idList)))+config.queryOrderBydateAndId
        #         cursor.execute(sql,idList)
        #         result = dictMerge(cursor.fetchall())

        self.render("index.html", articleList=result, startPage=pageNum + 1, totalPages=totalPages)


class DateList(BaseHandler):
    def get(self, *args, **kwargs):
        # print args
        pN = args[1]
        # 获取日期
        dt = datetime.strptime(args[0], "%Y-%m-%d")
        # 计算UTC时间
        eight = timedelta(hours=8)
        sixteen = timedelta(hours=16)
        start = (dt - eight).strftime("%Y-%m-%d %H:%M:%S")
        end = (dt + sixteen).strftime("%Y-%m-%d %H:%M:%S")

        sqlPre = config.queryAll \
                 + config.queryWhereByDateBetween \
                 + config.queryGroupByArticleId \
                 + config.queryOrderBydateAndId \
                 + config.queryByLimit
        # 获取分页结果和页码、总页数
        result, pageNum, totalPages = util.getPage(self.application.conn.cursor(),
                                                   sqlPre,
                                                   pN,
                                                   start, end)

        self.render("index.html", articleList=result, startPage=pageNum + 1, totalPages=totalPages)


class AddArticle(BaseHandler):
    """
    添加新文章
    """

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """
        显示添加页面
        :param args:
        :param kwargs:
        :return:
        """

        sqlCategory = config.queryAllCategory
        sqlTags = config.queryAllTags
        with self.application.conn.cursor() as cursor:
            cursor.execute(sqlCategory)
            categoryList = cursor.fetchall()
            cursor.execute(sqlTags)
            tagList = cursor.fetchall()

        self.render("addmarkdown.html", categoryList=categoryList, tagList=tagList)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """
        添加新文章
        :param args:
        :param kwargs:
        :return:
        """

        title = self.get_argument("title")
        content = re.sub(r'<br/?>', '\r\n', self.get_argument("content"))
        category = self.get_argument("category")

        if (title == "" or content == ""):
            self.flash(u"标题或内容不能为空哦", "info")
            self.redirect(self.reverse_url("addArticle"))
        else:
            date = datetime.now(pytz.utc)
            tags = self.get_arguments("tag")
            sqlInsertArticle = config.insertArticle
            sqlInsertArticleTags = config.insertTagsForArticle
            # 获取摘要
            summary=getMDSummary(content)

            with self.application.conn.cursor() as cursor:
                # 添加文章
                cursor.execute(sqlInsertArticle, (title, date, content, category,summary))
                result = cursor.lastrowid
                # self.application.conn.commit()
                # 添加文章关联标签
                if (len(tags) > 0):
                    cursor.executemany(sqlInsertArticleTags, zip([str(result)] * len(tags), tags))

            self.flash(u"添加成功", "success")
            self.redirect(self.reverse_url("articleDetail", result))


class ModifyArticle(BaseHandler):
    """
    修改文章
    """

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """
        获取修改页面
        :param args:
        :param kwargs:
        :return:
        """
        id = args[0]

        sql = config.queryAll.replace("summary","content") + config.queryWhereById + config.queryOrderBydateAndId
        sqlCategory = config.queryAllCategory
        sqlTags = config.queryAllTags

        with self.application.conn.cursor() as cursor:
            # 获取文章数据
            cursor.execute(sql, id)
            article = dictMerge(cursor.fetchall(), "id")[0]
            # 获取所有分类
            cursor.execute(sqlCategory)
            categoryList = cursor.fetchall()
            # 获取所有标签
            cursor.execute(sqlTags)
            tagList = cursor.fetchall()
        self.render('modifyarticle.html', article=article, categoryList=categoryList, tagList=tagList)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """
        修改文章
        """
        id = args[0]
        argument = {}
        # 处理参数,默认上传的都是列表形式的，个数为1的则转化为字符串
        for k in self.request.arguments:
            length = len(self.get_arguments(k))
            if (length == 1):
                if (self.get_argument(k) == ""):
                    self.redirect(self.reverse_url("ModifyArticle", id))
                    return
                argument[k] = re.sub(r'<br/?>', '\r\n', self.get_argument(k))
            elif (length > 1):
                argument[k] = self.get_arguments(k)
        # 创建摘要
        argument['summary']=getMDSummary(argument.get('content',''))
        sqlUpdateArticle = config.updateArticleByid
        sqlDeleteArticleTags = config.deleteTagsById
        sqlInsertArticleTags = config.insertTagsForArticle

        with self.application.conn.cursor() as cursor:
            # 修改文章

            cursor.execute(sqlUpdateArticle, argument)

            # self.application.conn.commit()
            # 添加文章关联标签
            tags = argument.get("tag")
            if tags and len(tags) > 0:
                cursor.execute(sqlDeleteArticleTags, argument.get("id"))
                cursor.executemany(sqlInsertArticleTags, zip([str(id)] * len(tags), tags))
        self.flash(u"修改成功", "success")
        self.redirect(self.reverse_url("articleDetail", id))


class DelArticle(BaseHandler):
    """
    删除文章
    """

    @tornado.web.authenticated
    def delete(self, *args, **kwargs):
        """
        删除文章
        :param args:
        :param kwargs:
        :return:
        """

        id = args[0]

        sqlCheckById = config.checkById
        sqlDeleteArticleById = config.delArticleByid
        sqlDeleteArticleTags = config.deleteTagsById
        with self.application.conn.cursor() as cursor:
            cursor.execute(sqlCheckById, id)
            result = cursor.fetchall()
            if len(result) < 1:
                self.flash(u"该文章不存在", "error")
                self.write("redirect")
                return
            # 删除文章关联标签
            cursor.execute(sqlDeleteArticleTags, id)
            # 删除文章
            cursor.execute(sqlDeleteArticleById, id)
            # self.application.conn.commit()

        self.flash(u"删除成功", "success")
        self.write("redirect")
