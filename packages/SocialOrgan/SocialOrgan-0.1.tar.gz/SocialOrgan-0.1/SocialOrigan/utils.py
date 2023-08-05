import asyncio
import os, sys
import time
import socket
import configparser
import json
import urllib.parse as up

import async_timeout
import aiosocks
import aiohttp

from termcolor import cprint
from requests import Session
from bs4 import BeautifulSoup
from aiosocks.connector import ProxyConnector, ProxyClientRequest


def load_config():
    c = configparser.ConfigParser()
    c.read(os.path.join("/usr/local/etc/SocialOrigan", "config.ini"))
    return c


Config = load_config()
ROOT = Config.get("path","ROOT")

def load_proxy(default=False, type_p=None):
    c = configparser.ConfigParser()
    if not os.path.exists(os.path.join(ROOT, "Proxy.ini")) or default:
        c.read(os.path.join(ROOT, "config.ini"))
        ProxyHostPort = c.get("proxy config", 'hostport')
        ProxyType = c.get("proxy config", 'type')
        return ProxyType + "://" + ProxyHostPort

    c.read(os.path.join(ROOT, "Proxy.ini"))
    proxies = []
    for i in range(len(c.sections())):
        s = c.get(str(i), 'hostport')
        t = c.get(str(i), 'type')
        if type_p:
            if type_p != t.lower().strip().split()[0]:
                continue

        if ' ' in t:
            t = t.strip().split()[0]

        proxies.append(t.lower()+"://"+s)

    return proxies

## session area
# sess will be a global variable
#  :: change , create, switch
#  
headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'

default_proxy = load_proxy(default=True)

Proxies = {
    'http': default_proxy,
    'https': default_proxy,
}


def Xml(resp):
    if hasattr(resp, 'content'):
        return BeautifulSoup(resp.text, 'lxml')
    else:
        return BeautifulSoup(resp, 'lxml')


######################
# check proxy if connected!
try:
    s = socket.socket()
    s.settimeout(7)
    _,host, port = default_proxy.split(":")
    host = host[2:]
    s.connect((host, int(port)))
except Exception as e:
    print(e)
    print("Local Proxy not Connected!", host, port)
    sys.exit(0)



class Sess:
    """
    auto_change_proxy_time: int
        timer can auto change proxy
    proxy: True/ str /list,
    label: a key to swich sess
    """
    _data = {}
    register_auto_change_proxy_key = set()

    def __init__(self, label, proxy=True, auto_change_proxy_time=0):
        self.sess = Session()
        self.label = label
        self.now_time = time.time()
        self.auto_change_proxy_time = auto_change_proxy_time
        
        self.sess.headers.update(headers)

        if proxy is True:
            self.sess.proxies.update(Proxies)
        elif isinstance(proxy, str):
            pro = {}
            t,h = proxy.split("://")
            if t == "socks5":
                proxy = t +"h://" + h
            pro['http'] = proxy
            pro['https'] = proxy
            self.sess.proxies.update(pro)

        elif isinstance(proxy, (list, tuple)):
            proxy['http'] = proxy[0]+ "://" + proxy[1]
            proxy['https'] = proxy[0]+ "://" + proxy[1]
            self.sess.proxies.update(proxy)

        self.Domain = ''

        if self.auto_change_proxy_time > 0:
            
            self.__class__.register_auto_change_proxy_key.add(self.label)


        self.__class__._data[label] = self

    def __del__(self):
        if self.label in self.__class__.register_auto_change_proxy_key:
            self.__class__.register_auto_change_proxy_key.remove(self.label)
        if self.label in self.__class__._data:
            del self.__class__._data[self.label]


    def set_proxy(self, proxy):
        n = time.time()
        if self.auto_change_proxy_time == 0:
            return False
        
        
        if (n - self.now_time) > self.auto_change_proxy_time:
            proxy = proxy.replace("5://","5h://")
            cprint("[+] proxy to " + self.label + "|" + proxy, 'green')
            self.sess.proxies['http'] = proxy
            self.sess.proxies['https'] = proxy
            self.now_time = n
        else:
            return False

    def test(self):
        ip = self.Get("http://ipv4.icanhazip.com").text
        # w = self.Get('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip=' + ip).json()
        # w = json.loads(w.split("=")[1][:-1])
        cprint('ip :' + ip, 'red')
        # print(w)
        # cprint('cou :' + w['country'], 'green')
        # cprint('province :' + w['province'], 'green')

    @classmethod
    def auto_change_proxy(cls):
        proxies = load_proxy()
        c = 0
        i = 0
        
        while c < len(cls.register_auto_change_proxy_key):
            p = proxies[i]
            sess = cls._data[list(cls.register_auto_change_proxy_key)[c]]
            c += 1
            if not sess.set_proxy(p):
                continue
            i+=1
                    

    def async_gets(self, urls, proxy=None):
        if not proxy:
            proxy = self.sess.proxies['https']
            proxy = proxy.replace('socks5h','socks5')

        res = Gets([[i, proxy] for i in urls])
        return res

    def async_downloads(self, urls, proxy=None):
        if not proxy:
            proxy = self.sess.proxies['https']
            proxy = proxy.replace('socks5h','socks5')

        res = Downloads([[[i, proxy], ''] for i in urls])
        return res


    def Get(self, url, **kargs):
        if self.auto_change_proxy_time > 0:
            self.__class__.auto_change_proxy()
        if not url.startswith("http"):
            url = up.urljoin(self.Domain, url)
        else:
            
            if  not self.Domain:
                p = up.urlparse(url)
                self.Domain = p.scheme + "://" + p.netloc

        return self.sess.get(url, **kargs)
        # return self.sess.get(url, verify=False,**kargs)

    def setDomain(self, domain):
        self.Domain = domain

    def Table(self, url, data=None, json=False):
        """
        json: xml  or json
        if data != None: will use Post, default use Get

        """
        if not hasattr(url, 'text') and isinstance(url, str):
            if data:

                res = self.Post(url, data)
            else:
                res = self.Get(url)

            if type == 'json':
                tmp = res.json()
                return tmp
            else:
                tmp = Xml(res.text)
        else:
            tmp = url

        
        tables = tmp.select("table")
        res = []
        for table in tables:
            rows = table.select("tr")
            headers = [col.text for col in rows[0].select("td") if hasattr(col, 'text')]
            if len(rows) <2:
                continue
            headers2 = [col.text for col in rows[1].select("td") if hasattr(col, 'text')]

            msgs = []
            for row in rows[1:]:
                values = [col.text for col in row.select("td") if hasattr(col, 'text') and col.text]
                if not values:
                    continue
                if len(values) != headers:
                    headers = headers2

                if len(values) / len(headers) < 0.3:
                    continue

                if values == headers:
                    continue
                msgs.append(dict(zip(headers, values)))

            yield msgs

    def Post(self, url, data):
        if self.auto_change_proxy_time > 0:
            self.__class__.auto_change_proxy()
        if not url.startswith("http"):
            url = up.urljoin(self.Domain, url)
        # return self.sess.post(url, data=data, verify=False)
        return self.sess.post(url, data=data, )

    def __getitem__(self, key):
        return self.__class__._data[key]




# import traceback


async def tcp_echo_client(num, host, loop):
    h, p = host.split(":")
    try:
        st = time.time()
        conner = asyncio.open_connection(h, int(p), loop=loop)
        reader, writer = await asyncio.wait_for(conner, timeout=7)
        et = time.time() -st
        # print('Close the socket')
        writer.close()
        return host,et

    except asyncio.TimeoutError:
        return host,9999
    except socket.error as e:
        # traceback.print_stack()
        return host,9999
    # print('Send: %r' % message)
    # writer.write(message.encode())

    # data = yield from reader.read(100)
    # print('Received: %r' % data.decode())


async def _tcp_test(hosts, loop):
    
    task = [tcp_echo_client(i, host, loop) for i, host in enumerate(hosts)]
    return await asyncio.gather(*task)



def TcpTests(hosts):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    res = loop.run_until_complete(_tcp_test(hosts, loop))
    loop.close()
    return [i for i in sorted(res, key=lambda x:x[1]) if i[1] < 100]



 
async def download_coroutine(session, url, filename='', proxy=None):
    with async_timeout.timeout(10):
        async with session.get(url, proxy=proxy) as response:
            if not response.status == 200:
                print("Some error")
                return await response.release()
            
            if not filename:
                filename = os.path.join("/tmp/",os.path.basename(url))
            try:
                with open(filename, 'wb') as f_handle:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f_handle.write(chunk)
            except Exception:
                os.remove(filename)
                print(url)
            return await response.release()
 
async def proxy_test(session, url, proxy):
    st = time.time()
    # cprint("[-] " + proxy + " --> " + url, 'yellow')
    try:
        with async_timeout.timeout(13):
            try:
                async with session.get(url, proxy=proxy) as response:
                    status = response.status
                    await response.release()
                    
                    if status == 200:
                        et = time.time() - st
                        cprint("[+]" + proxy + " "+str(et), "green")
            
                        
                        return proxy, et
                    else:
                        
                        return proxy, 9999

            except aiohttp.ClientOSError as e:
                # cprint(e, 'red')
                # cprint("[x] +proxy "+ proxy +" error", 'red')
                return proxy, 9998
            except aiohttp.ServerDisconnectedError as e:
                # cprint(e, 'red')
                # cprint("[x] + ServerDisconnectedError proxy " + proxy + " error", 'red')
                return proxy, 9997
            except Exception as e:
                return proxy, 9996
    except TimeoutError:
        return proxy, 1000
            

async def get_coroutine(session, url, proxy=None):

    with async_timeout.timeout(10):
        async with session.get(url, proxy=proxy) as response:
            if not response.status == 200:
                print("Some error")
                return await response.release()
            
            
            try:
                return await response.text()
            except Exception:
                return await response.release()
 



async def _run(loop, urls, download=False, test=False):
    # auth5 = aiosocks.Socks5Auth('proxyuser1', password='pwd')
    
    # ba = aiohttp.BasicAuth('login')

    # remote resolve
    conn = ProxyConnector()
 
    async with aiohttp.ClientSession(loop=loop, connector=conn, request_class=ProxyClientRequest) as session:
        if download:
            tasks = [download_coroutine(session, url[0], filename, proxy=url[1]) if isinstance(url, list) else  download_coroutine(session, url, filename) for url, filename in urls]
        elif test:
            tasks = [proxy_test(session, url, proxy) for url, proxy in urls]
        else:
            tasks = [get_coroutine(session, url[0], proxy=url[1]) if isinstance(urls, list) else get_coroutine(session, url)  for url in urls]
        return await asyncio.gather(*tasks)
 
def Downloads(urls):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        res = loop.run_until_complete(_run(loop, urls, download=True))
        loop.close()
        return res
    finally:
        loop.close()

def Gets(urls):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        res = loop.run_until_complete(_run(loop, urls))
        loop.close()
        return res
    finally:
        loop.close()


def ProxyTests(urls):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        res = loop.run_until_complete(_run(loop, urls, test=True))
        loop.close()
        return res
    finally:
        loop.close()



class OAuth:
    FORM_CSS_SELECT = []
    LOG_OUT_CSS_SELECT = []
    logined = {}

    def __init__(self,user, passwd, **kargs):
        self.user = user
        self.passwd = passwd
        self.data = {}
        self.method = 'post'

    def _check_form(self, field, type):
        selector = self.__class__.LOG_OUT_CSS_SELECT
        if type == 'login':
            selector = self.__class__.FORM_CSS_SELECT
        found = False
        for form_css_select in selector:
            if field.select(form_css_select):
                inputs = field.select(form_css_select)[0].select("input")
                self.method = field.select(form_css_select)[0].attrs['method']
                # self.data.update({i.attrs['name']:i.attrs['value']
                for i in inputs:
                    if 'name' not in i.attrs:
                        continue
                    if 'username' in i.attrs['name'] or 'email' in i.attrs['name']:
                        self.data[i.attrs['name']] = self.user
                    elif 'passwd' in i.attrs['name'] or 'password' in i.attrs['name']:
                        self.data[i.attrs['name']] = self.passwd
                        
                    if 'value' not in i.attrs:
                        continue

                    self.data[i.attrs['name']] = i.attrs['value']

                self.action = field.select(form_css_select)[0].attrs['action']
                found = True
                break
        return found

    def do_form(self, field, type='login', label=None):
        if self._check_form(field, type):

            if label:
                if not Sess._data[label].sess.cookies:
                    cprint("No cookie found !!!")
                sess = Sess._data[label]
                Post = sess.Post
                Get = sess.Get

            if self.method == 'post':
                return Post(self.action, self.data)
            else:
                return Get(self.action, self.data)
        else:
            print('nichts ist passiert !')

    def login(self, field, label=None, on_done=None, **kargs):
        self.data = kargs

        res = self.do_form(field, label=label)

        if on_done:
            if not hasattr(res, 'select') and hasattr(res, 'text'):
                res = Xml(res.text)
            return on_done(res)
        return res

    def logout(self, field, label=None, on_done=None,**kargs):
        self.data = kargs
        
        res =  self.do_form(field, 'logout',label=label)
        if on_done:
            if not hasattr(res, 'select') and hasattr(res, 'text'):
                res = Xml(res.text)
            return on_done(res)
        return res



# if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(loop))