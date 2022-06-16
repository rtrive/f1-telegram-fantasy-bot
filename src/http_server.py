import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


class PythonServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("GET request for {}".format(self.path).encode("utf-8"))


def start(log: logging.Logger, hostname: str, port: int):
    server = ThreadingHTTPServer((hostname, port), PythonServer)
    log.info(f"Server started at {hostname}:{port}")
    try:
        server = Thread(target=server.serve_forever)
        server.daemon = True
        server.start()

    except KeyboardInterrupt:
        server.server_close()
        log.info("Server stopped successfully")
