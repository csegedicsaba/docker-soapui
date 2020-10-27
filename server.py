#!/usr/bin/env python
from __future__ import print_function

import cgi
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        with open('server_index.html', 'r') as server_index:
            self.wfile.write(server_index.read().replace('\n', ''))


    def do_POST(self):
        # self._set_headers()
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        print("ctype: ", ctype)
        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.get('content-length'))
            postvars = parse.parse_qs(self.rfile.read(length), True)
        elif ctype == 'text/xml':
            length = int(self.headers.get('content-length'))
            postvars = parse.parse_qs(self.rfile.read(length), True)
        else:
            postvars = {}

        suite = postvars.get('suite')
        xml = postvars.get('project')
        properties = postvars.get('properties')
        option = postvars.get('option')
        load = postvars.get('load')
        loadTest = postvars.get('loadTest')


        if not xml:
            self.send_response(552, message='No SoapUI Project')
            self.end_headers()
            self.wfile.write('you need to specify the SoapUI project!')
            return
        else:
            xml = xml[0]

        print('project: ', xml)

        with open('/tmp/soapui-project.xml', 'wb') as w:
            w.write(xml)

        if load:
             arguments = ['/opt/SoapUI/bin/loadtestrunner.sh']
        else:
            arguments = ['/opt/SoapUI/bin/testrunner.sh']

        if suite:
            arguments.append('-s"%s"' % suite[0].decode(encoding='UTF-8'))

        if loadTest:
            arguments.append('-l"%s"' % loadTest[0].decode(encoding='UTF-8'))

        if option:
            for op in option:
                for line in op.decode(encoding='UTF-8').splitlines():
                    arguments.append('%s' % line)

        if properties:
            properties = properties[0].decode(encoding='UTF-8')
            f = open('/tmp/global.properties', 'w')
            print(properties, file=f)
            f.close()
            arguments.append('-Dsoapui.properties=/tmp/global.properties')

        arguments.append('/tmp/soapui-project.xml')

        print('arguments: ', arguments )

        p = Popen(arguments, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
        try:
            output, error = p.communicate()

            print('Error', error)
            print('Output', output)

            if p.returncode >= 1:
                self.send_response(550, message='Test Failure(s)')
                self.end_headers()
                self.wfile.write(output)
                self.wfile.write(error)
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output)

        except Exception as e:
            print('Exception', e)
            self.send_response(500)
            self.wfile.write(e)


def run(server_class=HTTPServer, handler_class=S, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('SoapUI Test Runner Started on port %s...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
