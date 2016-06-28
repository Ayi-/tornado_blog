# -*- coding:utf-8 -*-
import sys
import re
from tornado import gen

reload(sys)
sys.setdefaultencoding("utf8")

from bs4 import BeautifulSoup, element
import hashlib
import math
import pytz
import misaka as m
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
import tornado.web

__author__ = 'AE'


def dictMerge(items, keys="id"):
    """
    整合数据库查询结果：多个tag整合在一起
    :param items:字典数据列表
    :param key:字典数据唯一标识，如id
    :return:整合完成的字典
    """
    length = len(items)

    if (length > 0):
        result = []
        result.append(items[0])
        items.pop(0)

        for item in items:
            # 比较是否是同一个key的数据（如同一个id，但tag不同）
            # 当前索引的数据和结果集数据的最后一个数据比较
            if result[-1].get(keys) == (item.get(keys)):

                # 遍历每一个数据的内容
                for k, v in item.items():
                    if v == "" or v == None:
                        break
                    value = result[-1].get(k)
                    # 判断是否只有一个数据，
                    # 如果是则表明需要转换成列表并添加新的数据

                    if not isinstance(value, (list, tuple)):

                        if value != v:
                            result[-1][k] = [value, v]
                    else:
                        if v not in value:
                            result[-1][k].append(v)

            else:
                result.append(item)
        return result
    return items


def convertDate(date, tzinfoFrom="UTC", tzinfoTo=None):
    """
    转换时区
    :param date:
    :param tzinfoFrom: 原始时区，默认"UTC"
    :param tzinfoTo: 目标时区,默认使用配置的时区
    :return:
    """
    if not tzinfoTo:
        tzinfoTo = settings.tzinfo
    if tzinfoFrom == None:
        raise Exception("tzinfoFrom is None")
    tzFrom = pytz.timezone(tzinfoFrom)
    tzTo = pytz.timezone(tzinfoTo)

    try:
        dt = tzFrom.localize(date)
        return dt.astimezone(tzTo)
    except:
        return date.astimezone(tzinfoFrom)


def convertDateForTemplate(date, format):
    da = convertDate(date)
    return da.strftime(format)


def md5_for_file(f, block_size=2 ** 20):
    """
    计算文件MD5
    :param f:
    :param block_size:
    :return:
    """
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()


def getPage(cursor, sqlPre, pageNum, *args):
    """
    分页，返回结果
    :param cursor:
    :param sqlPre: 查询sql
    :param pageNum: 分页参数
    :param args: 参数
    :return:结果集，页码,总页数
    """
    with cursor:
        # 计算分页偏移量
        if pageNum == "":
            pN = 0
        else:
            pN = int(pageNum) - 1
            if pageNum < 0:
                pN = 0
        offset = settings.pageLimit * pN

        # 获取ID
        argslist = list(args)
        argslist.append(settings.pageLimit)
        argslist.append(offset)
        cursor.execute(sqlPre, argslist)
        result = cursor.fetchall()
        idList = [item['id'] for item in result]  # [49, 50, 48, 47, 46, 45, 44, 43, 37, 36]

        # 获取总数量
        cursor.execute(settings.queryCount)
        totalPages = math.ceil((cursor.fetchone().values()[0]) / settings.pageLimit)
        if (len(idList) < 1):
            result = None
        else:
            # 批量查询
            sql = settings.queryAll \
                  + settings.queryWhereInById % ', '.join(list(map(lambda x: '%s', idList))) \
                  + settings.queryOrderBydateAndId
            cursor.execute(sql, idList)
            result = dictMerge(cursor.fetchall())
    return result, pN, totalPages


def getSummary(html, Limitlength=500):
    """
    获取文章摘要
    :param html: 原本内容
    :param Limitlength:限制长度
    :return:
    """
    result = ""
    soup = BeautifulSoup(html, "html.parser")
    # 去除所有span标签
    # for tag in soup.find_all('span'):
    #     tag.unwrap()

    # 获取第一个节点
    node = soup.children.next()
    while (node and len(result) <= Limitlength):
        # img,pre标签特殊处理

        if (node.name in ('img', 'pre')):
            # 获取长度
            if len(result) + len(node.text) <= Limitlength:
                # Limitlength+=len(str(node))
                # print len(node.text)
                result += node.decode() + '<br/>'
                # 下一个标签

                if (node.next_sibling):
                    node = node.next_sibling
                else:
                    node = node.previous_element.next_sibling
            else:
                break
        elif (type(node) == element.NavigableString):
            if len(result) + len(node) <= Limitlength:
                # Limitlength+=len(str(node))
                result = result + node.string
                # 下一个标签
                node = node.next_element
                if type(node) == element.Tag and node.name != 'span':
                    result += '<br/>'
            else:
                result = result + node.string[:Limitlength - len(result)] + '&nbsp;'
                break
        else:
            # 下一个节点
            node = node.next_element
    return result


# markdown代码高亮渲染
class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(
                tornado.escape.url_escape(text.strip()))

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(cssclass="monokai")

        return highlight(text, lexer, formatter)


# markdown渲染
renderer = HighlighterRenderer()
md = m.Markdown(renderer, extensions=('fenced-code',))

def getMDSummary(mdText):
    """
    获取markdown的html摘要
    :param mdText: markdown文本
    :return:
    """
    return getSummary(md(mdText))

from settings import settings