#coding:utf-8

import time, hashlib
import tornado.web
import tornado.auth
from tornado.web import HTTPError
from base import BaseHandler
from session import session


class UsersHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.get_current_user().channel:
            raise HTTPError(403)

        wid = self.get_current_user().wid
        users = self.db.query(
            "select a.wid, a.username, b.orderdest from lem_webowner a left join lem_ivr_info b on a.wid = b.channel where a.channel = %s order by a.regtime desc",
            wid)

        localdata = getLocalData(self.db, wid, None)
        self.render("admin/users.html", menuType="users", entries=users, **localdata)


class PaymentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        wid = self.get_current_user().wid
        channel = self.get_current_user().channel
        page = self.get_intargument("page", 1)
        ordercode = self.get_argument("ordercode", "")
        beginDate = self.get_argument("beginDate", "")
        endDate = self.get_argument("endDate", "")
        pagesize = 15
        if page < 1:
            page = 1
        start = (page - 1) * pagesize
        cond = "  and 1=1"
        if beginDate != '' and endDate != '':
            cond = " and  billdate between '" + beginDate + "' and '" + endDate + "'"

        if channel is None:
            if ordercode == '':
                entries = self.db.query(
                    "SELECT * FROM lez_webowner_bill where wid = %s " + cond + " ORDER BY billdate DESC LIMIT %s, %s",
                    wid, start,
                    pagesize)

                total = self.db.getint("SELECT count(*) from lez_webowner_bill where wid = %s " + cond + "", wid)
                turnpage = "admin/payment.html"
            else:
                entries = self.db.query(
                    "SELECT l.subdate,l.showcount,l.showincome,i.feenum "
                    "FROM lez_bill_day l,lem_ivr_info i where l.wid = %s and l.servicecode=i.servicecode and i.feenum=%s "
                    + cond + "ORDER BY subdate DESC LIMIT %s, %s",
                    wid, ordercode, start,
                    pagesize)

                total = self.db.getint("SELECT count(*) from lez_webowner_bill where wid = %s" + cond + "", wid)
                turnpage = "admin/payment3.html"
        else:
            if ordercode == '':
                entries = self.db.query(
                    "SELECT * FROM lez_webowner_channel_day where wid = %s and channel = %s ORDER BY subdate DESC LIMIT %s, %s",
                    channel, wid, start, pagesize)

                total = self.db.getint("SELECT count(*) from lez_webowner_channel_day where wid = %s and channel = %s ",
                                       channel, wid)
                turnpage = "admin/payment2.html"
            else:
                entries = self.db.query(
                    "SELECT l.subdate,l.showcount,l.showincome,i.feenum "
                    "FROM lez_bill_day l,lem_ivr_info i where l.wid = %s and l.servicecode=i.servicecode and i.feenum=%s and l.channel=%s "
                    "ORDER BY subdate DESC LIMIT %s, %s", wid, ordercode, channel, start,
                    pagesize)

                total = self.db.getint("SELECT count(*) from lez_webowner_bill where wid = %s", wid)
                turnpage = "admin/payment4.html"

        pagination = getPagination(page, total, pagesize)
        localdata = dict(getLocalData(self.db, wid, channel), **pagination)
        self.render(turnpage, menuType="payment", entries=entries, **localdata)


class ChannelPaymentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.get_current_user().channel:
            raise HTTPError(403)

        wid = self.get_current_user().wid
        page = self.get_intargument("page", 1)
        pagesize = 15
        if page < 1:
            page = 1
        start = (page - 1) * pagesize

        entries = self.db.query("SELECT * FROM lez_webowner_channel_day where wid = %s ORDER BY subdate "
                                "DESC LIMIT %s, %s", wid, start, pagesize)

        total = self.db.getint("select count(*) from lez_webowner_channel_day where wid = %s", wid)

        pagination = getPagination(page, total, pagesize)
        localdata = dict(getLocalData(self.db, wid, None), **pagination)
        self.render("admin/channelPayment.html", menuType="channelPayment", entries=entries, **localdata)


class IVRDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        wid = self.get_current_user().wid
        channel = self.get_current_user().channel
        page = self.get_intargument("page", 1)
        pagesize = 15
        if page < 1:
            page = 1
        start = (page - 1) * pagesize
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if channel is None:
            total = self.db.getint(
                "select count(*) from lez_service_log where wid = %s and subtime >= %s and feeflag = 1", wid, today)
            entries = self.db.query(
                "SELECT * FROM lez_service_log where wid = %s and subtime >= %s and feeflag = 1 ORDER BY subtime DESC LIMIT %s, %s",
                wid, today, start, pagesize)
        else:
            total = self.db.getint(
                "select count(*) from lez_service_log where wid = %s and channel = %s and subtime >= %s and feeflag = 1",
                channel, wid, today)
            entries = self.db.query(
                "SELECT * FROM lez_service_log where wid = %s and channel = %s and subtime >= %s and feeflag = 1 ORDER BY subtime DESC LIMIT %s, %s",
                channel, wid, today, start, pagesize)

        pagination = getPagination(page, total, pagesize)
        localdata = dict(getLocalData(self.db, wid, channel), **pagination)
        self.render("admin/ivrdetail.html", menuType="ivrdetail", entries=entries, **localdata)


def getPagination(page, total, pagesize):
    interval = 2
    totalPage = total / pagesize + 1
    page = 1 if page < 1 else page
    page = totalPage if page > totalPage else page
    hasNextPage = page < totalPage
    hasPrevPage = page > 1
    nextPage = page + 1 if hasNextPage else totalPage
    prevPage = page - 1 if hasPrevPage else 1
    minPage = page - interval if page > interval else 1
    maxPage = page + interval if page < totalPage - interval else totalPage

    pagination = dict(
        page=page,
        totalPage=totalPage,
        hasNextPage=hasNextPage,
        hasPrevPage=hasPrevPage,
        nextPage=nextPage,
        prevPage=prevPage,
        minPage=minPage,
        maxPage=maxPage,
    )
    return pagination


def getLocalData(db, wid, channel):
    #String showincome = Strings.trimFloat(DbUtils.getValue("select sum(showincome) as showincome from lez_webowner_bill where wid = ? and payflag = 0", wid));
    #String lastincome = Strings.trimFloat(DbUtils.getValue("select sum(showincome) as showincome from lez_webowner_bill where wid = ? and billdate = ?", wid, yesterday));
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    if channel is None:
        showincome = db.get(
            "SELECT sum(showincome) as showincome from lez_webowner_bill where wid = %s and payflag = 0",
            wid).showincome
        todayincome = db.get(
            "SELECT sum(feeincome) as feeincome from lez_service_log where wid = %s and feeflag = 1 and subtime >= %s",
            wid, today).feeincome
    else:
        todayincome = db.get(
            "SELECT sum(feeincome) as feeincome from lez_service_log where wid = %s and channel = %s and feeflag = 1 and subtime >= %s",
            channel, wid, today).feeincome
        showincome = 0
    paydata = dict(
        todayincome=todayincome,
        showincome=showincome,
    )
    return paydata


class ModifyPwdHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        loginuser = self.session.get("username")
        username = self.get_argument("username", loginuser)
        if username != loginuser and loginuser != "admin":
            raise HTTPError(403)

        wid = self.get_current_user().wid
        channel = self.get_current_user().channel
        localdata = getLocalData(self.db, wid, channel)
        self.render("admin/modifyPwd.html", menuType="modifyPwd", username=username, **localdata)

    @tornado.web.authenticated
    @session
    def post(self):
        wid = self.get_current_user().wid
        password = self.get_argument("password")
        if wid is None:
            raise HTTPError(403)
        if password is None or len(password) < 4:
            tipmessages = "请输入密码."
        else:
            self.db.execute("update lem_webowner set password = %s where wid = %s", hashlib.md5(password).hexdigest(),
                            wid)
            tipmessages = "密码修改成功."

        if len(tipmessages) > 0:
            self.addMessages(tipmessages)

        self.session.remove("username")
        self.addMessages("密码修改成功, 请重新登录!")
        self.redirect("/")


class AuthLoginHandler(BaseHandler):
    def get(self):
        next = self.get_argument("next", "/user/payment")
        self.render("admin/login.html", next=next)

    @session
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        tipmessages = ""
        if (len(username) <= 0 or len(password) <= 0):
            tipmessages = "请输入用户名和密码!"
        else:
            author = self.db.get("SELECT * FROM lem_webowner WHERE username = %s",
                                 username)
            if not author:
                tipmessages = "用户不存在!"
            elif hashlib.md5(password).hexdigest() != author.password:
                tipmessages = "密码错误!"
            else:
                self.session.set("username", str(author.username))

        next = self.get_argument("next", "/user/payment")
        if len(tipmessages) > 0:
            self.addMessages(tipmessages)
            self.render("admin/login.html", next=next)
        else:
            self.redirect(next)


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("sessionid")
        self.redirect(self.get_argument("next", "/"))


class PageNotFoundHandler(BaseHandler):
    def get(self):
        raise tornado.web.HTTPError(404)


handlers = [
    (r"/", AuthLoginHandler),
    (r"/auth/logout", AuthLogoutHandler),
    (r"/user/payment", PaymentHandler),
    (r"/user/channelPayment", ChannelPaymentHandler),
    (r"/user/ivrdetail", IVRDetailHandler),
    (r"/user/users", UsersHandler),
    (r"/user/modifyPwd", ModifyPwdHandler),
    (r'.*', PageNotFoundHandler),
]
