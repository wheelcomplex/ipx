
#
#    git clone https://github.com/out0fmemory/qqwry.dat
#    pip3 install qqwry-py3 dnspython
#    pip3 install ping3
#    pip3 install pyinfo

#   /usr/bin/python3 /home/vhost/ipx.sh/qqwry_http.py
#
#   /usr/bin/screen -dmS 'qqwry_http' /bin/sh -c '/usr/bin/python3 /home/vhost/ipx.sh/qqwry_http.py'
#


from threading import Thread
#from SocketServer import ThreadingMixIn
#from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

import socket
import dns.resolver
from ping3 import ping, verbose_ping

from qqwry import QQwry
import json



q = QQwry()
q.load_file('/home/vhost/ipx.sh/htdocs/qqwry.dat/qqwry_lastest.dat', loadindex = True)


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.headers.get('X-Real-IP')

        dns_list = {
            "cn"       : "114.114.114.114",
            "cn-cm-gd" : "117.50.11.11",
            "google"   : "8.8.8.8"
        }

        ping_node_list = {
            "cn"       : "114.114.114.114",
            "cn-cm-gd" : "117.50.11.11",
            "google"   : "8.8.8.8"
        }

        result = ''

        try:
            location = ''
            provider = ''
            if self.path == '/ip' or self.path == '/json' or self.path == '/xml':
                (location, provider) = q.lookup(ip)
                location = location.replace('CZ88.NET','None')
                provider = provider.replace('CZ88.NET','None')

            if self.path == 'i':
                import pyinfo

                result = json.dumps(pyinfo.python_info())
            elif self.path == '/ip' or self.path == '/json':
                result = '{"ip":"%s","location":"%s", "provider":"%s"}' % (ip, location, provider)
            elif self.path == '/xml':
                result = '<?xml version="1.0" encoding="UTF-8"?><data><ip>%s</ip><location>%s</location><provider>%s</provider></data>' % (ip, location, provider)
            elif self.path == '/ptr':
                result, alias, addresslist = socket.gethostbyaddr(ip)
            elif self.path.startswith('/a/'):
                default_dns = '117.50.11.11' #'211.136.192.6'  china-mobile-zhihai

                query_list = self.path.split('/')
                if len(query_list) < 3:
                    raise

                query_domain = query_list[2]
                query_dns = default_dns

                ip_list = []

                if len(query_list) == 4:
                    try:
                        if dns_list.get(query_list[3], False):
                            query_dns = dns_list.get(query_list[3])
                        else:
                            query_dns = None
                            result = 'Invaild DNS Node!'
                    except:
                        query_dns = None
                        result = 'Invaild DNS Node!'
                
                if query_dns is not None:
                    dns_resolver = dns.resolver.Resolver()
                    dns_resolver.nameservers = ['%s' % query_dns]

                    for rdata in dns_resolver.query(query_domain, 'A') :
                        ip_addr = str(rdata)

                        if ip_addr not in ip_list:
                            ip_list.append(ip_addr)
                    result = ','.join(ip_list)

                    print(query_domain)
                    print(query_dns)

            elif self.path.startswith('/ping/'):
                ping_node_name = 'sg'

                ping_list = self.path.split('/')
                if len(ping_list) < 3:
                    raise

                ping_target = ping_list[2]
                local_ping = True



                if len(ping_list) == 4:
                    local_ping = False

                    try:
                        if ping_node_list.get(ping_list[3], False):
                            ping_node_ip = ping_node_list.get(ping_list[3])

                            ping_node_name = ping_list[3]

                            result = '[%s] result from %s' % (ping_target, ping_node_ip)

                            #result = curl('http://ping_node_ip/ping/%s' % ping_target)
                        else:
                            result = 'Invaild Ping Node!'
                    except:
                        pass

                if local_ping:
                    domain_ip = ''
                    if is_valid_ipv4_address(ping_target):
                        domain_ip = ping_target
                    else:
                        domain_ip = socket.gethostbyname(ping_target)
                        
                    result = "%s#%sms@%s" % (domain_ip, str(round(float(ping(ping_target, timeout=10, unit='ms')), 2)), ping_node_name)
            else:
                result = ''
        except Exception as err:
            print("Error: {0}".format(err))

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(result.encode())

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def serve_on_port(port):
    server = ThreadingHTTPServer(("localhost",port), Handler)
    server.serve_forever()

Thread(target=serve_on_port, args=[1111]).start()
serve_on_port(2222)


