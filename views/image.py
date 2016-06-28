#-*- coding:utf-8 -*-
import sys
import uuid
import os
from pip._vendor.requests import Response
from settings import settings as config
from views.util import md5_for_file

reload(sys)
sys.setdefaultencoding("utf8")

from datetime import datetime
from views.index import BaseHandler
__author__ = 'AE'

UPLOAD_FOLDER = '/TmageUploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

#文件名合法性验证
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class ImageUpload(BaseHandler):
    """
    富文本编辑器上传图片
    """
    # 取消XSRF检查
    def check_xsrf_cookie(self):
        pass
    def post(self, *args, **kwargs):
        fileinfo = self.request.files['wangEditorH5File'][0]
        if fileinfo in (None,""):
            result = r"error|未成功获取文件，上传失败"
            self.finish(result)
        else:

            if fileinfo and allowed_file(fileinfo.filename):
                filename = str(uuid.uuid1())+"."+fileinfo["content_type"].split("/")[-1]
                # print filename

                # 设置当前日期
                dt = datetime.now().strftime("%Y%m%d")
                # print dt
                # 创建图片保存地址
                staticPath = os.path.join(config.UPLOAD_IMAGE_FOLDER,dt)
                imgdir = os.path.join(config.settings.get("static_path"),
                                      staticPath)

                # print staticPath
                #print imgdir
                if(not os.path.exists(imgdir)):
                    os.makedirs(imgdir)
                with open(os.path.join(imgdir,filename),'wb') as fp:      #有些文件需要已二进制的形式存储，实际中可以更改
                    fp.write(fileinfo['body'])

                imgUrl = self.static_url(os.path.join(staticPath,filename))
                # print imgUrl
                self.finish(imgUrl)