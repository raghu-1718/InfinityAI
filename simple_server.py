from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello World')

if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 8003), SimpleHandler)
    print('Server running on port 8003')
    server.serve_forever()
