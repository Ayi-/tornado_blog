# -*- coding:utf-8 -*-
from views import uimodules

__author__ = 'AE'

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = {
    # 静态文件地址
    "static_path": os.path.join(os.path.dirname(__file__, ), os.path.pardir, "static"),
    "template_path": os.path.join(os.path.dirname(__file__), os.path.pardir, "templates"),
    "gzip": True,
    "debug": True,
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "xsrf_cookies":True,
    "login_url": "/login",
    "ui_modules": uimodules
}

#设置端口监听
WEB_PORT=8001
# 数据库配置
DATABASES={
"host":"127.0.0.1", # 数据库主机ip
"port":3306,  # 端口
"database":"spring_blog",  # 数据库名称
"user":"root",  # 用户名
"password":"0000",  # 密码
}

# 上传文件目录
UPLOAD_IMAGE_FOLDER = 'img/'
# 时区
tzinfo ='Asia/Shanghai'

# SQL_CALC_FOUND_ROWS用来记录查询结果的数量
# SELECT FOUND_ROWS();来获取结果
# 查询所有，包含外键
queryAll = """ SELECT SQL_CALC_FOUND_ROWS
    article.id,
    article.title,
    article.date,
    article.summary,
    category.id category_id,
    category.name category_name,
    tags.id tags_id,
    tags.name tags_name
    FROM article
    LEFT OUTER JOIN category ON article.category = category.id
    LEFT OUTER JOIN article_tags ON article.id = article_tags.article_id
    LEFT OUTER JOIN tags ON article_tags.tags_id = tags.id
    """
queryCount = """ SELECT FOUND_ROWS() """
pageLimit = 10.0
queryGroupByArticleId = """ group by article.id """
queryByLimit = """ limit %s offset %s"""
# ID查询文章
queryWhereById = """ where article.id=%s """
queryWhereInById = """ where article.id in (%s) """

# 根据文章分类查询
queryWhereByCategoryID = """ where article.category=category.id AND category.id=%s """

# 根据日期查询
queryWhereByDate = """ where date like %s """
queryWhereByDateBetween = """ where date between %s and %s """

# TAG查询文章
queryWhereByTagID = """where article.id  in (select article_id from article_tags where article_tags.tags_id=%s) """
# 根据日期和id排序
queryOrderBydateAndId = """ ORDER BY article.date desc ,article.id asc """

# 查询所有文章分类
queryAllCategory = """ SELECT * FROM category """

# 查询所有标签
queryAllTags = """ SELECT * FROM tags """

# 添加文章
insertArticle = """Insert into article (title,date,content,category,summary) value(%s,%s,%s,%s,%s)"""
# 添加TAG关联
insertTagsForArticle = """INSERT INTO article_tags (article_id,tags_id) VALUES(%s,%s)"""

# 删除关联的TAG
deleteTagsById = """delete from article_tags where article_id = %s"""

# 更新文章
updateArticleByid = """update article set title=%(title)s,
                        date=%(date)s,
                        content=%(content)s,
                        category=%(category)s,
                        summary=%(summary)s
                        where id = %(id)s"""

delArticleByid = """DELETE FROM article WHERE id=%s"""

checkById = """select id from article where id=%s"""
