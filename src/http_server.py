import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

PORT = 8080
HOSTNAME = "0.0.0.0"


class PythonServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("GET request for {}".format(self.path).encode("utf-8"))


def start(log: logging.Logger):
    server = ThreadingHTTPServer((HOSTNAME, PORT), PythonServer)
    log.info(f"Server started at port {PORT}")
    try:
        server = Thread(target=server.serve_forever)
        server.daemon = True
        server.start()

    except KeyboardInterrupt:
        server.server_close()
        log.info("Server stopped successfully")
