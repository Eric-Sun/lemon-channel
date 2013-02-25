# -*- encoding: utf-8 -*-

import time,json
from tornado.web import RequestHandler
from session import session

class BaseHandler(RequestHandler):
    _start_time = time.time()
    _finish_time = None
    _tipmessages = None

    def write_error(self, status_code, **kwargs):
        import traceback
        if self.settings.get("debug") and "exc_info" in kwargs:
            exc_info = kwargs["exc_info"]
            trace_info = ''.join(["%s<br/>" % line for line in traceback.format_exception(*exc_info)])
            request_info = ''.join(["<strong>%s</strong>: %s<br/>" % (k, self.request.__dict__[k]) for k in self.request.__dict__.keys()])
            error = exc_info[1]
            
            self.set_header('Content-Type', 'text/html')
            self.finish("""<html>
                             <title>%s</title>
                             <body>
                                <h2>Error</h2>
                                <p>%s</p>
                             </body>
                           </html>""" % (error, error))

    def request_time(self):
        """Returns the amount of time it took for this request to execute."""
        if self._finish_time is None:
            return time.time() - self._start_time
        else:
            return self._finish_time - self._start_time
        
    def json_write(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

    def get_intargument(self, argName, defaultVal=None):
        val = self.get_argument(argName, defaultVal)
        if val:
            return int(val)
        elif val == None:
            return None
        else:
            return 0

    @property
    def db(self):
        return self.application.db

    @property
    def uploaddir(self):
        return self.application.uploaddir
    
    @session
    def addMessages(self, msg):
        tipmessages = self.session.get("tipmessages")
        if not tipmessages:
            tipmessages = ""
        tipmessages = msg
        self.session.set("tipmessages", tipmessages)
        
    @session
    def getMessages(self):
        if not self._tipmessages:
            self._tipmessages = self.session.get("tipmessages")
            if not self._tipmessages:
                self._tipmessages = ""
            self.session.remove("tipmessages")
        return self._tipmessages
        
    @session
    def get_current_user(self):
        username = self.session.get("username")
        if not username:
            #print 'session insert guangdong8899!'
            #self.session.set("username", 'guangdong8899')
            #return self.db.get("SELECT * FROM lem_webowner WHERE username = %s", 'guangdong8899')
            return None
        return self.db.get("SELECT * FROM lem_webowner WHERE username = %s and status = 1", username)
