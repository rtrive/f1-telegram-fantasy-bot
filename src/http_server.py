import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

logger = logging.getLogger(__name__)

PORT = 8080
HOSTNAME = "localhost"


class PythonServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        logging.info("request GET / ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("GET request for {}".format(self.path).encode("utf-8"))


def start():
    server = ThreadingHTTPServer((HOSTNAME, PORT), PythonServer)
    logger.info(f"Server started at port {PORT}")
    try:
        server = Thread(target=server.serve_forever)
        server.daemon = True
        server.start()

    except KeyboardInterrupt:
        server.server_close()
        logger.info("Server stopped successfully")
