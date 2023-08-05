import sys
import time

from .users import Mail
from .utils import Xml
from .utils import load_proxy
from FlowWork.Net.flownet import  FLowNet
from termcolor import cprint


PAYLOAD = """
https://twitter.com/signup
INPUT#full-name/I'{name}'
INPUT#email/I'{email}'
INPUT#password/I'{passwd}'
.sign-up-box/C
2
.skip-link/C
1
li>button/C
.sign-up-box/C
.StartCongratulations-buttons>a/C
1
.PillList-item>input/C
.StartActions>button/C
.js-skip-step/C
1
.StartActions>button/C
.js-close[Not now]/C
1
.js-close[Skip all]/C
.resend-confirmation-email-link/C
[over]"""


def register_one(start_time=None,f=None, m=None):
    if not start_time:
        start_time = time.time()
    if not m:
        m = Mail()

    cprint("Email:" + m.address , 'green')
    name = m.address.split("@")[0]
    passwd = m.address[:-1]
    email = m.address
    cprint("Generate account:"+ " | ".join([name, email, passwd]), "red")
    cprint("patch scripts ...", 'red')
    text= PAYLOAD
    text = text.format(name=name, email=email, passwd = passwd).split("\n")
    cprint("Initialize Browser .... ",'red', end='')
    if not f:
        # proxy_one = load_proxy(type_p='socks5')[0]
        proxy_one = "socks5://127.0.0.1:1080"
        f = FLowNet(proxy=proxy_one, driver='chrome')
    time.sleep(1)

    cprint(" Ok", 'green', attrs=['bold'])
    cprint("........................................", 'blue')
    try:
        for cmd in text:
            if not cmd.strip():continue
            f.flow_doc(cmd)
    except Exception as e:
        cprint(str(e), "red")
        f.phantom.close()
    else:
        with open("account.txt", "a") as fp:
            fp.write(":".join([name, email, passwd])+ "\n")
        cprint("Confirm .... ", 'yellow', end='')
        while 1:
            m.table()
            res = m.read('Confirm')
            if not res:
                cprint(".", 'yellow', end='')
                continue
            tmp =  Xml(res.text).text
            hs = tmp.find("replace(\"")
            if hs != -1:
                e_str = tmp[hs + 9: -2].replace("\\", "")
            f.go(e_str)
            break
    f.phantom.close()
    return email, passwd

def main():
    start_time = time.time()
    m = Mail()
    f = FLowNet(proxy='socks5://127.0.0.1:1080', driver='chrome')
    email, passwd = register_one()
    cprint("[registe  Over ... confirm account ..]", 'red')

    while 1:
        c = input("[press to continue]").strip()
        if c == 'q':
            cprint("Bye ~~")
            sys.exit(0)
        now = (time.time() - start_time) / 60
        if now > 9:
            m.more_10_minute()
        m.table()
        res = m.read(0)
        if not res:
            cprint("........................................", 'blue')
            continue
        tmp =  Xml(res.text).text
        hs = tmp.find("replace(\"")
        if hs != -1:
            e_str = tmp[hs + 9: -2].replace("\\", "")
            cprint("Go ? : " + e_str, 'green')
            c = input(" >>>>>[Y/no] Y")
            if not c or c == 'Y':
                f.go(e_str)

        cprint("........................................", 'yellow')

if __name__ == '__main__':
    main()