#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
import os, sys, websocket, gevent, time, traceback, geventwebsocket
from collections import *
from future.utils import viewitems

class WebSocket(websocket.WebSocket): receive = websocket.WebSocket.recv

__version__ = "1.6.1"

Channels = defaultdict(list)

def sendv(msgs, ws): [ws.send(msg) for msg in msgs]

def publishv(msgv, wsx = None, channel_name = "0"):
    for ws in Channels[channel_name] + Channels['ALL']:
        if ws != wsx:
            try:    sendv(msgv, ws)
            except: traceback.print_exc()

def conn(addr = "127.0.0.1:8080/"):
    print("Connecting to", addr)
    ws = WebSocket()
    ws.connect("ws://" + addr)
    return ws

def subscribev(ws, ch_names, verbose = False):
    if not ch_names:
        return
    if verbose:
        print("Subscribing to ", ch_names)
    for ch in ch_names:
        Channels[ch].append(ws)

def unsubscribe_all(ws):
    for name, ch in viewitems(Channels):
        try: ch.remove(ws)
        except ValueError: pass

def _loop_ws(ws):
    while 1:
        msg1 = ws.receive()
        if msg1 is None:
            break
        elif msg1.startswith("sub "):
            ch_names = msg1[4:].split()
            subscribev(ws, ch_names)
        elif msg1.startswith("pub .w"):
            msg2 = int(ws.receive())
            msg3 = ws.receive()
            print('='*80)
            from pprint import pprint
            pprint(Channels)
            print('='*80)
        elif msg1.startswith("pub CTL"):
            msg2 = int(ws.receive())
            msg3 = ws.receive()
            if msg3.startswith('.w'):
                print('='*80)
                from pprint import pprint
                pprint(Channels)
                print('='*80)
            else:
                print('?'*80)
                print(msg3)
                print('?'*80)
        elif msg1.startswith("pub "):
            msg2 = int(ws.receive())
            msg3 = ws.receive()
            print("The msgs were was: %r" % repr((msg1, msg2, msg3)))
            if msg2:
                raw_ch = msg1[4:]
                arr = raw_ch.split('/')
                publishv([msg1, str(msg2 - 1), msg3], ws, arr[0])
        else:
            print("BAD CMD", msg1)
            ws.send("bad cmd")
            break

def loop_ws(ws, channels = []):
    try:
        subscribev(ws, [str(id(ws)), "0"] + channels)
        _loop_ws(ws)
    finally:
        unsubscribe_all(ws)

def tmain(addr = "echo.websocket.org"):
    while 1:
        try:
            print(repr(addr))
            ws = conn(addr)
            loop_ws(ws)
            ws.close()
        except:
            traceback.print_exc()
            time.sleep(1)

def serve():
    port = int(sys.argv[1])
    try:    addr = sys.argv[2]
    except: addr = ''
    if addr: t2 = gevent.spawn(tmain, addr)
    def ws_app(env, start):
        try:
            loop_ws( env["wsgi.websocket"] )
            return []
        except KeyError:
            msg = 'Not a Websocket'
            start('500 ' + msg, [('Content-type', 'text/html')])
            return [msg,'\n']
    print("Serving port %s..." % port)
    geventwebsocket.WebSocketServer(("", port), ws_app).serve_forever()

def pub():
    data = sys.stdin.read()
    ws = conn(sys.argv[1])
    try:    ch = sys.argv[2]
    except: ch = '0'
    sendv(['pub ' + ch, '2', data], ws)
    ws.close()
    time.sleep(0.1)

def sub():
    ws = conn(sys.argv[1])
    #channel_list = [str(id(ws)), "0"] + sys.argv[2:]
    channel_list = sys.argv[2:]
    msg = "sub "+' '.join(channel_list)
    ws.send(msg)
    loop_ws(ws)
    
def _main():
    if    sys.argv[0].endswith('p2svr'): serve(); exit(0)
    elif  sys.argv[0].endswith('p2pub'): pub()  ; exit(0)
    elif  sys.argv[0].endswith('p2sub'): sub()  ; exit(0)

def main(): _main() ; sys.argv.pop(0) ; main() ; print("NO") ; exit(1)
    
if __name__ == '__main__': main()
