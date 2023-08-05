"""
Sever classes used in the web method
"""

import io
import json
import logging
import os
import socketserver
import time
from http import server
from threading import Condition

import Pyro4

from edurov.utils import server_ip, detect_pi

if detect_pi():
    import picamera


class StreamingOutput(object):
    """Defines output for the picamera, used by request server"""

    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
            self.count += 1
        return self.buffer.write(buf)


class RequestHandler(server.BaseHTTPRequestHandler):
    """Request server, handles request from the browser"""
    output = None
    keys = None
    rov = None
    base_folder = None
    index_file = None

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/stream.mjpg':
            self.serve_stream()
        elif self.path.startswith('/sensordata.json'):
            self.serve_sensor()
        else:
            path = os.path.join(self.base_folder, self.path[1:])
            if os.path.isfile(path):
                self.serve_path(path)
            else:
                self.send_404()

    def do_POST(self):
        if self.path.startswith('/keys.json'):
            content_len = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_len).decode('utf-8')
            json_obj = json.loads(post_body)
            self.keys.set_from_js_dict(json_obj)
            self.send_response(200)
            self.end_headers()
        elif self.path.startswith('/stop'):
            self.send_response(200)
            self.end_headers()
            self.rov.run = False
        else:
            self.send_404()

    def serve_path(self, path):
        if 'style.css' in path:
            content_type = 'text/css'
        elif 'script.js' in path:
            content_type = 'text/javascript'
        else:
            content_type = 'text/html'
        with open(path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def send_404(self):
        self.send_error(404)
        self.end_headers()

    def serve_sensor(self):
        sensor_values = json.dumps(self.rov.sensor)
        content = sensor_values.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def serve_stream(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type',
                         'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while True:
                with self.output.condition:
                    self.output.condition.wait()
                    frame = self.output.frame
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning(
                'Removed streaming client %s: %s',
                self.client_address, str(e))

    def log_message(self, format, *args):
        return


class WebpageServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """Threaded HTTP server, forwards request to the RequestHandlerClass"""
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, stream_output,
                 rov_proxy, keys_proxy, index_file=None, debug=False):
        self.start = time.time()
        self.debug = debug
        RequestHandlerClass.output = stream_output
        RequestHandlerClass.rov = rov_proxy
        RequestHandlerClass.keys = keys_proxy
        RequestHandlerClass.base_folder = os.path.abspath(
            os.path.dirname(index_file))
        RequestHandlerClass.index_file = index_file
        super(WebpageServer, self).__init__(server_address,
                                            RequestHandlerClass)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Shutting down http server')
        if self.debug:
            finish = time.time()
            frame_count = self.RequestHandlerClass.output.count
            print('Sent {} images in {:.1f} seconds at {:.2f} fps'
                  .format(frame_count,
                          finish - self.start,
                          frame_count / (finish - self.start)))


def start_http_server(video_resolution, fps, server_port, index_file,
                      debug=False):
    if debug:
        print('Using {} @ {} fps'.format(video_resolution, fps))

    with picamera.PiCamera(resolution=video_resolution,
                           framerate=fps) as camera, \
            Pyro4.Proxy("PYRONAME:ROVSyncer") as rov, \
            Pyro4.Proxy("PYRONAME:KeyManager") as keys:
        stream_output = StreamingOutput()
        camera.start_recording(stream_output, format='mjpeg')
        try:
            with WebpageServer(server_address=('', server_port),
                               RequestHandlerClass=RequestHandler,
                               stream_output=stream_output,
                               debug=debug,
                               rov_proxy=rov,
                               keys_proxy=keys,
                               index_file=index_file) as server:
                print('Visit the webpage at {}'.format(server_ip(server_port)))
                server.serve_forever()
        finally:
            print('closing web server')
            camera.stop_recording()
