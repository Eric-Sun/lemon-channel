from tornado.options import define

mysql_settings = dict(
    host="localhost",
    user="lemon",
    passwd="lemon001)(",
    db="lemon",
)

database_types = dict(
    mysql=mysql_settings
)

define("port", default=8881, help="run on the given port", type=int)
define("database", default="mysql", help="choose your database type")
