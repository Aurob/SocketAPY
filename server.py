import socket
import json, re, sys
from _thread import *
import threading

#Helper function for simplyfing byte conversion
def as_bytes(data):
    return bytes(data, encoding="utf-8")

class server:
    
    #__Initialize values and begin main thread (wording?)__
    def __init__(self, path, ip, port):
        self.BASE = path
        self.HOST = ip
        self.PORT = int(port)
        self.BUFFER = 1024
        self.restypes = {
            'js' : 'text/html',
            'html' : 'text/html',
            'text' : 'text/plain',
            'bmp' : 'image/jpeg',
            'json' : 'application/json'
        }
        self.thread_lock = threading.Lock()
        
    #__Start the server, handle valid api requests only__
    def start_server(self):
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            print("Server started...")
            
            while 1:
                conn, addr = s.accept()
                data = conn.recv(self.BUFFER).decode("utf-8") 
                #Send an initial OK response
                conn.send(b'HTTP/1.0 200 OK\r\n')
                
                request = data.splitlines()[0] #request info
                url = request.split()

                base = url[1].split('/')
                if base[1] != self.BASE:
                    self.error(conn, 'Valid request url must start with /'+self.BASE+'/')
                else:
                    #begin new thread
                    self.thread_lock.acquire()
                    start_new_thread(self.handle_query, (''.join(base[2:]),conn,))
                    
    #__Response helper functions__
    def send(self, conn, retval, restype):
        if restype == 'json':
            retval = json.dumps(retval)
        conn.send(as_bytes('Content-Type: '+self.restypes[restype]+'\r\n\r\n'))
        conn.send(as_bytes(retval))
        #close connection
        conn.close()
        
    def error(self, conn, e):
        self.send(conn, {"error":str(e)}, 'json')
        
    #__Endpoint resolution__
    def handle_query(self, data, conn):
        retval = {}
        
        #get the query items
        request = re.findall('\w+', data)
        #if no endpoint is specified, default to the 'test' endpoint
        endpoint = None
        query = None

        #query endpoint
        if len(request) > 0:
           endpoint = request[0]
        #query paramaters
        if len(request) > 1:
            query = request[1]

        retval['query'] = query
        if endpoint:
            try:
                restype, retval = eval("self."+endpoint)(query, retval, conn)
                self.send(conn, retval, restype)

            #Catch any errors that occur in the endpoint methods
            except Exception as e:
                self.error(conn, e)
        else:
            self.error(conn, 'No endpoint specified')
            
        #End thread
        self.thread_lock.release()

    #__Endpoint Methods__
    def test(self, query, retval, conn):
        if query == 'failure':
            raise Exception('test failure success')
        elif query == 'success':
            retval['test'] = "test success"
        return 'json', retval
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = 'api'
        ip = 'localhost'
        port = 1234
    else:
        path = sys.argv[1]
        ip = sys.argv[2]
        port = sys.argv[3]
    #start the server
    s = server(path, ip, port)
    s.start_server()
