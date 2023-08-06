from Pyiiko.server import *
from Pyiiko.frontWeb import *

iiko = IikoServer(ip='operaderbent.iiko.it', port="8080",
                  login='admin', password='resto#test')
front = FrontWebAPI(url="", moduleid="", content_type={
                    "content-type": "application/json"})
