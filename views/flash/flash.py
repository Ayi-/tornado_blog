import sys

reload(sys)
sys.setdefaultencoding("utf8")

import tornado.web
import re
import pickle
from tornado.escape import to_unicode
from tornado import web, escape


class FlashHandler(object):
    """
    Extends Tornado's RequestHandler by adding flash functionality.
    and GetFlash in UIModule
    """

    def flash(self, message, category='info'):
        """write by Flask.Flash
        Flashes a message to the next request.  In order to remove the
        flashed message from the session and to display it to the user

        :param message: the message to be flashed.
        :param category: the category for the message.  The following values
                     are recommended: ``'error'`` for errors, ``'info'`` for
                      information messages,``'success'`` for success info and
                       ``'warning'`` for warnings.  However any kind of string
                        can be used as category.
        """
        # get request._flashes
        self._flashes = self._flashes or []
        self._flashes.append((category,message))
        result = pickle.dumps(self._flashes)
        self.set_cookie('flashes_cookies', tornado.escape.url_escape(result))
