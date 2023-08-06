# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient


class WsClient(WebSocketClient):
    def opened(self):
        self.send("ls")

    def closed(self, code, reason):
        print "Closed down", code, reason

    def received_message(self, m):
        # print("=> %d %s" % (len(m), str(m)))
        print str(m)
        if len(m) == 175:
            self.close(reason='Bye bye')

# if __name__ == '__main__':
#     try:
#         ws = WsClient('ws://10.131.40.141/webtty/i444-phpmyadmin.a1.huayun.local:59999/eyJhbGciOiJIUzUxMiJ9'
#                       '.eyJqdGkiOiI4MjMyMTYxZS0zNzc5LTQ5OWUtOWE1Zi01YzUxYzIzNTkxOTkiLCJzdWIiOiIxNCIsImlzcyI6IiIsIml'
#                       'hdCI6MTUxOTcwNDAxMCwiZXhwIjoxNTE5NzA0MDcwfQ.CUFdVWZKA1ZTfnNd4E0ToiGFn2JV2kR4YLPgLas1p-_4p5BXSz'
#                       'gvvYOuw-4QQKjLdf7_Xb2V2iAX-SClk2iFVg/eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIzZjUzMWM4NC1hZTcwLTQzNWUtO'
#                       'TY1Yy03Y2EwY2UwYTcxODkiLCJzdWIiOiIiLCJpc3MiOiIiLCJpYXQiOjE1MTk3MDQwMTAsImV4cCI6MTUxOTcwNDA3MH0.'
#                       'DFWX_aX-qTz98bMvobaugF2PAIAMsmXDaBLmdcQl-9SX52m5bsBXNhLAdDwcTuLOkdkuAe0f9Sczs9fKmACGJQ/ws',
#                       protocols=['webtty'])
#         ws.connect()
#         ws.run_forever()
#     except KeyboardInterrupt:
#         ws.close()