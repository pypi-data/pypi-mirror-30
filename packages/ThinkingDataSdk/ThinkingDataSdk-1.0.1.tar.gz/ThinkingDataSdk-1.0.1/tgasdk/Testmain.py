#encoding:utf-8
import datetime
from tgasdk.sdk import TGAnalytics, BatchConsumer, LoggingConsumer, AsyncBatchConsumer

# tga = TGAnalytics(AsyncBatchConsumer("server_uri","appid"))
tga = TGAnalytics(BatchConsumer("http://10.25.38.223:44444/logagent","quanjie-python-sdk"))
# tga = TGAnalytics(LoggingConsumer("F:/home/sdk/log"))


properties = {
    "#time":'2018-01-12 20:46:56',
    "#ip":"192.168.1.1",
    "Product_Name":"a",
    '#os':'windows'
}

tga.track('dis',None,"shopping",properties)

properties = {
    "#time":datetime.datetime.now(),
    "#ip":"192.168.1.1",
    "name":"sfjiahdj",
    "age":18

}
tga.user_setOnce(distinct_id="niming_user1",properties=properties)

properties = {
    "#time":datetime.datetime.now(),
    "#ip":"192.168.1.1",
    "age":2,
}
tga.user_add(distinct_id="niming_user1",properties=properties)
# tga.close()






