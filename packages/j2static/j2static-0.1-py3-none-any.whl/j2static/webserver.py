#! /usr/bin/env python3
##
# Dynamic server mode
#
# This is useful for development because you can see the changes made
# in real time.
##

import pathlib
import mimetypes
import shutil

import jinja2
from j2static.build import get_builder

from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
TEMPLATE_DIR = "_templates/"

class TemplateHTTPServer(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        file_path = self.path
        if file_path[-1] == "/":
            file_path += "index.html"

        builder = get_builder("html", TEMPLATE_DIR)
        if builder.filter(file_path):
            try:
                data = builder.render(file_path)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

            except jinja2.TemplateNotFound as e:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                data = "{e} does not exist as a template".format(e=e)
            except jinja2.TemplateSyntaxError as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                data = "<h1>template error</h1> <p>{e.name}, line {e.lineno}: <samp>{e.message}</samp></p>".format(e=e)
            self.wfile.write(data.encode())
        else:
            fpath = pathlib.Path(TEMPLATE_DIR) / pathlib.Path(file_path[1:])
            print(fpath.resolve())
            if not fpath.exists():
               self.send_response(404)
               data = "not valid page"
            else:
               mime, enc = mimetypes.guess_type(str(fpath))
               self.send_response(200)
               self.send_header('content-type', mime)
               self.end_headers()
               with open(fpath, 'rb') as content:
                   shutil.copyfileobj(content, self.wfile)



def serve(args):
    Handler = TemplateHTTPServer
    httpd = HTTPServer(('', PORT), Handler)
    print("webpage will be served on http://localhost:8080")
    httpd.serve_forever()
