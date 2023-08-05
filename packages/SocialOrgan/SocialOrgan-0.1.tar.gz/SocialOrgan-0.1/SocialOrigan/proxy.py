import sys,os
import re
import json
import time
import configparser

from .utils import Gets, Sess, Xml, TcpTests, ProxyTests
from .utils import load_config
from .utils import load_proxy
import execjs
from termcolor import cprint

PROXY_HOSTS = "http://premiumproxy.net/"
Config = load_config()
sess = Sess("proxy")
ROOT = Config.get("path", "ROOT")
class Data:
    pass

class Premiumproxy:
    codes = json.load(open(os.path.join(ROOT, "country_code.json")))

    def __init__(self, num='hk', types=''):
        coun, num = self.__class__.codes[num.upper()].split(":")
        self.data = {
            'tldc':num,
            'anmm':2,
            'vlast':0,
            'eport':'',
            'submit':'Search'
        }


    def pull(self,country):
        coun, self.data['tldc'] = self.__class__.codes[country.upper()].split(":")
        print(coun)
        if type == "socks":
            self.base = Xml(sess.Get("http://premiumproxy.net/socks-proxy-list.php").text)
        else:    
            self.base = Xml(sess.Post("http://premiumproxy.net/search-proxy.php", data=self.data).text)

    def load(self, country='all'):
        cprint("[-] Pull data from server ...", 'red')
        self.pull(country)
        
        cprint("[-] Load js Context...", 'red')
        self.get_js_context()

        cprint("[+] update proxy list ...", 'green')
        self.proxy = self.get_proxy_list()
        if self.proxy:
            cprint("[-] test proxy server speed ....", 'red')
            self.test_proxy_connect()
            time.sleep(1)
            cprint("[-] test proxy connect to Google's speed ....", 'red')
            self.test_proxy_google()

    def parse(self, i):

        i = i[1:-1]
        f,l = i.split("^")
        return self.e.__dict__[f] ^ self.e.__dict__[l]

    def get_js_context(self):
        t = 0
        while  1:
            
            try:
                s = self.base.select("script")[5].text.split("eval(")[1].strip()[:-1]
                self.js_context =  execjs.eval(s)
                e = Data()
                exec(self.js_context)
                for i in self.js_context.split(";"):
                    if not i.strip(): continue

                    k , v = i.split("=")
                    try:   
                        setattr(e, k, eval(v))
                    except NameError:
                        f, l = v.split("^")

                        if re.match('\d', f):
                            f = "e." + f

                        if re.match('\d', l):
                            l = "e." + l



                        setattr(e,k, eval(f+"^" + l))

                    
                self.e = e
                break
            except IndexError as e:
                t += 1
                cprint("the page is error, ... try %d time" % t, "red")
                cprint("[-] Pull again ...", 'red')
                self.pull(country='All')
                if t >= 5:
                    cprint("reload failed !! ", "red")
                    break
                continue

    def test_proxy_google(self):
        proxyies = load_proxy()
        proxies = [['https://www.google.com',i] for i in  load_proxy() if not i.startswith("https")]
        tmp =  ProxyTests(proxies)
        test_res = [i for i in tmp if i[1] < 20 ]
        sort_proxy = sorted(test_res, key=lambda x:x[1])
        config = configparser.ConfigParser()
        for i,e  in enumerate(sort_proxy):
            t,p = e[0].split("://")
            config[str(i)] = {
                'hostport':p,
                'type':t.upper(),
                'speed': e[1]
            }

        cprint("[+] sorted proxy to Proxy.ini", 'green', attrs=['bold'])
        with open(os.path.join(ROOT, 'Proxy.ini'), 'w') as fp:
            config.write(fp)

    def test_proxy_connect(self):
        d = {i['Proxy address:port']:i['Proxy type'] for i in self.proxy}
        res = TcpTests(d.keys())
        config = configparser.ConfigParser()
        for i,e  in enumerate(res):
            config[str(i)] = {
                'hostport':e[0],
                'type':d[e[0]],
                'speed': e[1]
            }

        cprint("[+] cache proxy to Proxy.ini", 'green', attrs=['bold'])
        with open(os.path.join(ROOT, 'Proxy.ini'), 'w') as fp:
            config.write(fp)


    def choose_a_proxy(self):
        p_type = Config.get('proxy '+ str(num), 'type')
        p_host_port = Config.get('proxy '+ str(num), 'hostport')
        return p_type, p_host_port


    def get_proxy_list(self):
        tables = sess.Table(self.base)

        for i in tables:
            if len(i) > 30:
                k = 'Proxy address:port'

                table = i
                st = time.time()
                for row in table:
                    host_port = row[k]
                    
                    if 'document' not in host_port:
                        continue
                    b = host_port.split()[1]
                    a = b.split("document")[0]
                    row[k] = a + ":" + ''.join([ str(self.parse(ii)) for ii in re.findall(r'(\([\w\^]*\))', host_port)])
                    # print(row[k])
                et = time.time() -st
                print("Use time: ", et)
                return table
        cprint("no proxy found ? ", 'red')
        return False

def main(country='all', help=False):
    if help:
        for i in Premiumproxy.codes:
            cprint(i, 'green')
        return
    if country.upper() not in Premiumproxy.codes:
        return
        
    p = Premiumproxy()
    p.load(country)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 1:
        main()
            
