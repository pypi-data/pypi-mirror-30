import socket, sys, os, re, time, datetime
import random
from functools import partial


from .utils import Downloads, Gets
from .utils import load_config
from .utils import Sess
from .utils import Xml
from .utils import OAuth
from .utils import load_proxy
from .utils import up
from .utils import headers
from termcolor import cprint
from qlib.data import dbobj, Cache


tmp_dir = '/tmp/twitter'
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

text_dir = os.path.join(tmp_dir, 'tw_text')
if not os.path.exists(text_dir):
    os.mkdir(text_dir)

img_dir = os.path.join(tmp_dir, 'tw_img')
if not os.path.exists(img_dir):
    os.mkdir(img_dir)

cache = Cache(os.path.join(tmp_dir, 'users.db'))




sess = Sess('default')
sess_label = 'default'
Sessions = {'default': sess}


def switch_session(label, new=False, **kargs):
    global sess
    global sess_label
    global Sessions

    if label not in Sessions or new is True:
        nsess = Sess(label)
        Sessions[sess_label] = sess
        sess_label = label
        sess = nsess
    else:
        sess_label = label
        sess = Sessions[sess_label]

def Get(url, reset=False, **kargs):
    if not url.startswith("http"):
        url = up.urljoin(Domain, url)
    if reset:
        switch_session(sess_label, new=True)
    return sess.Get(url, **kargs)

def Post(url, data):
    if not url.startswith("http"):
        url = up.urljoin(Domain, url)
    return sess.Post(url, data=data)

## meta area
BASE_URL = "https://twitter.com/"
tw_Url = lambda x: up.urljoin(BASE_URL, x)
open_tw = lambda u: Xml(Get(tw_Url(u)).text)




def time_match(str_time):
    now = time.localtime()
    year = now.tm_year
    mon = now.tm_mon
    day = now.tm_mday
    hour = now.tm_hour
    minu = now.tm_min
    sec = now.tm_sec

    if re.search(r"^(\d{0,4}\-?\d+\-\d+)\s?(\d{0,4}\-?\d+\-\d+)?$", str_time):
            str_time = str_time.strip()
            if ' ' in str_time:
                s,e = str_time.split(' ')
                st = time.strptime(s, '%Y-%m-%d') if s.count('-') == 2 else time.strptime(str(now.tm_year) + '-' + s, '%Y-%m-%d')
                et = time.strptime(e, '%Y-%m-%d') if s.count('-') == 2 else time.strptime(str(now.tm_year) + '-' + e, '%Y-%m-%d')
            else:
                st = time.strptime(str_time, '%Y-%m-%d') if str_time.count('-') == 2 else time.strptime(str(now.tm_year) + '-' + str_time, '%Y-%m-%d')
                et = now
            return time.mktime(st), time.mktime(et)
            
    elif re.search(r'^\d+\s+(day|year|mon|hour)\s+(ago)$' , str_time.strip()):
        num,e ,_  = str_time.split()
        if e == 'year':
            year -= int(num)
        elif e == 'mon':
            mon -= int(num)
        elif e == 'day':
            day -= int(num)
        elif e == 'hour':
            hour -= int(num)

        stamp = datetime.datetime(year, mon, day, hour, minu, sec).timestamp()
        return stamp, time.mktime(now)


class DownCache(dbobj):
    pass

class User(dbobj):
    """
    self.nick = nick
    self.id = id
    self.follow 
    """
    
    def follower(self):
        users = c.query(User, account =self.account)
        return users


class UserCard:
    Data = []
    Data_id = []

    def __init__(self, user_field='', name=None, account=None, desc=None, img_head=None, img_background=None):
        if name and account and desc:
            self.name = name
            self.account = account
            self.desc = desc
            self.img_head = img_head
            self.img_background = img_background

        else:
            try:
                name_a =  user_field.select("a.fullname")[0]

                self.name = name_a.text
                #get account and  extract  'xxxx' from '/xxxx'
                self.account = name_a.attrs['href'][1:]
            except IndexError:
                self.name = user_field.select(".ProfileHeaderCard-nameLink")[0].text
                self.account = user_field.select("b.u-linkComplex-target")[0].text


            try:
                self.desc = user_field.select(".ProfileCard-bio")[0].text
            except IndexError:
                self.desc = user_field.select(".ProfileHeaderCard-bio")[0].text
            
        if self.account not in self.__class__.Data_id:
            self.__class__.Data.append(self)
            self.__class__.Data_id.append(self.account)

    def to_user(self):
        return User(account=self.account, name=self.name, desc=self.desc)

    
    @classmethod
    def load(cls):
        us =  cache.query(User)
        c = 0
        for u in us:
            if u.account not in UserCard.Data_id:
                instance = cls(name=u.name, account=u.account, desc=u.desc)
                c += 1
        print("Load : %d"%c, 'data!')

    @staticmethod
    def save(cache):
        c = 0
        n = []
        ids = [ u.account for u in  cache.query(User)]
        for i in UserCard.Data:
            
            if not i.account in ids:
                n.append(i)
                continue
            c += 1
        cache.save_all(*[i.to_user() for i in n])
        print("Save : %d" % c , "data!")

    # def __del__(self):
    #     self.__class__.save(cache)

    def __getitem__(self, item_id_or_index_or_account_or_time):
        if isinstance(item_id_or_index_or_account_or_time, int):
            return self.__class__.Data[item_id_or_index_or_account_or_time]
        elif isinstance(item_id_or_index_or_account_or_time, str):
            s = []    
            for i in self.__class__.Data:
                if item_id_or_index_or_account_or_time in i.account:
                    s.append(i)
            return s



class Msg(dbobj):
    
    def save_text(self):
        if hasattr(self, 'text'):
            with open(os.path.join(tmp_dir, self.item_id), 'w') as fp:
                fp.write(self.text)


class MessageCard:
    Data = []
    Data_id = []

    def __init__(self, msg_field='', sender='', pub_time=None, item_id=None, name=None, account=None, text='', quote='', media='', retw=0):
        if item_id and name and account:
            self.item_id = item_id
            self.name = name
            self.sender = sender
            self.pub_time = int(pub_time)
            self.account = account
            self.quote = quote
            self.media = media
            self.text = text
            self.retw = retw

        else:
            self.item_id = msg_field.attrs['data-item-id']
            
            self.sender = sender

            # header 
            name_group = msg_field.select('a.account-group')
            if name_group:
                name_group = name_group[0]
            self.pub_time = int(msg_field.select('span.js-short-timestamp')[0].attrs['data-time'])
            self.name = name_group.text
            self.account = name_group.attrs['href'][1:]
            

            # text area
            self.text_group = msg_field.select('.js-tweet-text-container')[0]
            self.text = self.text_group.text

            
            # quote
            self.quote = ''
            quote = msg_field.select('a.QuoteTweet-link')
            if quote:
                self.quote = quote[0].attrs['data-conversation-id']

            # media
            self.media = ''
            m = msg_field.select('.js-macaw-cards-iframe-container')
            if m:
                self.media = m[0].attrs['data-card-url']

            self.retw = 1 if sender != self.account else 0

        if self.item_id not in self.__class__.Data_id:
            self.__class__.Data.append(self)
            self.__class__.Data_id.append(self.item_id)




    def to_db(self):
        return Msg(item_id=self.item_id, sender=self.sender, name=self.name, account=self.account, retw=self.retw, pub_time=int(self.pub_time), quote=self.quote, media=self.media)


    def __repr__(self):
        return '|'.join([self.sender, "tw : ", self.item_id, self.name ,self.account])

    @staticmethod
    def save(cache):
        c = 0
        ids = [ u.item_id for u in  cache.query(Msg)]
        n = []
        for i in MessageCard.Data:
            
            if i.item_id not in ids:
                n.append(i)
                c += 1
                continue

            
        _cache = [i.to_db() for i in n]
        cache.save_all(*_cache)
        print("Save : %d" % c , "data!")
        [i.save_text() for i in _cache]


    @classmethod
    def load(cls):
        us =  cache.query(Msg)
        c = 0
        for u in us:
            if u.item_id not in MessageCard.Data_id:
                instance = cls(item_id= u.item_id, name=u.name, pub_time=u.pub_time, account=u.account, retw=u.retw, sender=u.sender, quote=u.quote, media=u.media)
                if os.path.exists(os.path.join(text_dir, u.item_id)):
                    text = ''
                    with open(os.path.join(text_dir, u.item_id)) as fp:
                        text = fp.read()
                    instance.text = text

                c += 1
        print("Load : %d"%c, 'data!')

    # def __del__(self):
    #     self.__class__.save(cache)

    def __getitem__(self, item_id_or_index_or_account_or_time):
        if isinstance(item_id_or_index_or_account_or_time, int):
            return self.__class__.Data[item_id_or_index_or_account_or_time]
        elif isinstance(item_id_or_index_or_account_or_time, str):
            s = []
            if re.match(r'^\d{10,18}$',item_id_or_index_or_account_or_time):
                
                for num, i in enumerate(self.__class__.Data_id):
                    if item_id_or_index_or_account_or_time in i:
                        s.append(self.__class__.Data[num])
                return s

            elif time_match(item_id_or_index_or_account_or_time):
                stamps = time_match(item_id_or_index_or_account_or_time)
                st = min(stamps)
                et = max(stamps)

                for i in self.__class__.Data:
                    if i.pub_time > st and i.pub_time < et:
                        s.append(i)
                return s
            else:
                for i in self.__class__.Data:
                    if item_id_or_index_or_account_or_time in i.account:
                        s.append(i)
                return s





class TwitterAuth(OAuth):
    BASE_URL = "https://twitter.com/"
    
    FORM_CSS_SELECT = [
        'form.LoginForm',
        'form.js-signin',
    ]

    LOG_OUT_CSS_SELECT = [
        'signout-form',
    ]

    

    def login(self, tw_panel):
        return super().login(tw_panel.tw, tw_panel.sess_label, on_done=tw_panel.check_access)

    def logout(self, tw_panel):
        return super().login(tw_panel.tw, tw_panel.sess_label)        


class TwitterPanel:

    def __init__(self, user, account=None, name=None, msg_pos=None, follow_pos=None, new_session=False, proxy=True):
        self.sess_label = 'twitter|' + user
        if new_session:
            self.sess_label = 'twitter' + str(time.time())
        self.follow_pos = 0
        self.max_position = 0
        if proxy == 'pub':
            proxy = random.choice(load_proxy()[:10])
        self.sess = Sess(self.sess_label, proxy=proxy)
        
        if account:
            self.account = account
            self.name = name
            self.max_position = msg_pos
            self.follow_pos = follow_pos
            self.tw = None
        else:
            self.tw = Xml(self.sess.Get(tw_Url(user)).text)
            self.account = user
            self.name = self.tw.select('a.ProfileHeaderCard-nameLink')[0].text.strip()
            self.max_position = self.tw.select(".stream-container")[0].attrs['data-max-position']
            self.desc = self.tw.select('.ProfileHeaderCard-bio')[0].text

            # load user..
            u = UserCard(self.tw.select(".ProfileHeaderCard")[0])
            # load user's img
            img_head = self.tw.select("img.ProfileAvatar-image")[0].attrs['src']
            u.img_head = img_head



    def follower(self, deep=3):
        if self.follow_pos == 0:
            b_follow_ur = '/%s/following' % self.account
            users = []
            init = Xml(self.sess.Get(b_follow_ur).text)
            if not self.check_access(init):
                return
            ## init followers
            position = init.select(".GridTimeline-items")[0].attrs['data-min-position']
            if int(position) < int(self.follow_pos):
                position = str(self.follow_pos)

            for w in init.select(".ProfileCard"):
                u = UserCard(w)
                print(u.name)

        headers = self.sess.sess.headers
        headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://twitter.com/%s/following" % self.account
        })
        #next
        position = self.follow_pos
        for i in range(deep):
            # print(i, 'turn', end='\r')
            follow_ur = '/%s/following/users?include_available_features=1&include_entities=1&max_position=%s&reset_error_state=false' % (self.account, position)
            res = self.sess.Get(tw_Url(follow_ur), headers=headers).json()
            
            position = res['min_position']
            if not res['has_more_items']:
                print(position)
                break
            new_users = Xml(res['items_html']).select('.ProfileCard')
            
            for w in new_users:
                u = UserCard(w)
                print(i,'/',u.name.strip(), end='\r')
            self.follow_pos = position

    def message(self, deep=5):
        msg_count = 0
        if self.tw:
            # init msg card , if load cache will skip this.
            if not self.check_access(self.tw):
                return
            messgs = self.tw.select('li.stream-item')
            for msg in messgs:
                name_group = msg.select('a.account-group')
                if not name_group:
                    continue
                pub_item = msg.select('span.js-short-timestamp')
                if not pub_item:
                    continue

                MessageCard(msg, self.account)
                msg_count += 1

        position = self.max_position
        # more 
        headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://twitter.com/%s" % self.account
        })

        for i in range(deep):
            more_msg = '/i/profiles/show/ggreenwald/timeline/tweets?include_available_features=1&include_entities=1&max_position=%s&reset_error_state=false' %  self.max_position
            u = tw_Url(more_msg)
            res = self.sess.Get(tw_Url(u), headers=headers).json()
            # yield res
            
            position = res['min_position']
            if not res['has_more_items']:
                print(res['min_position'])
                break
            for msg in Xml(res['items_html']).select('li.stream-item'):
                name_group = msg.select('a.account-group')
                if not name_group:
                    continue
                pub_item = msg.select('span.js-short-timestamp')
                if not pub_item:
                    continue

                MessageCard(msg, self.account)
                msg_count += 1
            print( msg_count,'/',i+1, 'turn', end='\r')
            self.max_position = position

    def check_access(self ,login_res):

        forms = login_res.select("form")
        for f in forms:
            if 'action' not in f.attrs:
                continue

            if f.attrs['action'] == '/account/access':
                cprint('may account: %s is Limited!!' % self.auth.user)
                return False
        return True

    @classmethod
    def load(cls, user='', load_all=False):
        '''
        if user == '':
            will load all user!!

        if load_all:
            will load all data include MessagCard, UserCard.
        '''
        if not user:
            users = cache.query(User)
            ts = []
            for user in users:
                ts.append(TwitterPanel.load(user.account, load_all=load_all))
            return ts

        o = cache.query_one(User, account=user)
        if not o:
            print("Not found user:%s in local DB." % user)
            return 

        d = cache.query_one(DownCache, account=user)
        if load_all:
            print("MessageCard load.")
            MessageCard.load()
            print("UserCard load.")
            UserCard.load()

        return TwitterPanel(o.account, 
            account=o.account,
            name=o.name,
            msg_pos=d.msg_pos,
            follow_pos=d.follow_pos)

    def __getitem__(self, key):
        """
        key:  
            'u:xxx' = search UserCard
            'm:xxx' = search MessageCard
                xxx : can be replace with a fuzy account, a name
                    if in 'm:' mode:
                        xxx can be use a time str like:
                            '222 day ago ' , '1 year ago' ,'12-2' , '2016-1-1 3-2' (2016-1-1 ~ now)

        """
        if ':' not in key:
            raise KeyError("""
            key:  
            'u:xxx' = search UserCard
            'm:xxx' = search MessageCard
                xxx : can be replace with a fuzy account, a name
                    if in 'm:' mode:
                        xxx can be use a time str like:
                            '222 day ago ' , '1 year ago' ,'12-2' , '2016-1-1 3-2' (2016-1-1 ~ now)
            """)

        mode, key = key.split(":")
        if re.search(r'^\d*$', key):
            key = int(key)

        if mode == 'm':
            return MessageCard.Data[0][key]

        elif mode == 'u':
            return UserCard.Data[0][key]


    def load_cache(self):
        o = cache.query_one(DownCache, account=self.account)
        if o:
            self.max_position = o.msg_pos
            self.follow_pos = o.follow_pos


        MessageCard.load()
        UserCard.load()

    def save_cache(self):
        o = cache.query_one(DownCache, account=self.account)
        
        # save cache data
        MessageCard.save(cache)
        UserCard.save(cache)

        if not o:
            w = DownCache(account= self.account, msg_pos=self.max_position, follow_pos=self.follow_pos)
            w.save(cache)
            return

        fo_pos = o.follow_pos
        msg_pos = o.msg_pos
        changed = False
        if msg_pos < int(self.max_position):
            msg_pos = self.max_position
            changed = True

        if fo_pos < int(self.follow_pos):
            fo_pos = self.follow_pos
            changed = True

        if changed:
            w = DownCache(account= self.account, msg_pos=str(msg_pos), follow_pos=str(fo_pos))
            cache.delete(o)
            cache.save(w)

    def login(self, user,passwd):
        self.auth = TwitterAuth(user, passwd)
        return self.auth.login(self)

    def logout(self):
        if hasattr(self, 'auth'):
            return self.auth.logout(self)

    @classmethod
    def Login(cls, user,passwd):
        t = cls('NBA')
        t.login(user, passwd)
        return t


    def __del__(self):
        
        self.logout()

class Mail:

    def __init__(self):
        self.sess = Sess("mail")
        self.menu = Xml(self.sess.Get('https://10minutemail.net/').text)
        self.start_time = time.time()
        self.address = 'X'
        address_area = self.menu.select(".mailtext")
        if address_area:
            self.address = address_area[0].attrs['value']

        self.recve = []

    def table(self):
        rows = iter(Xml(self.sess.Get("https://10minutemail.net/mailbox.ajax.php").text).select("table")[0])
        # rows = iter(self.menu.select("table"))
        headers = [col.text for col in next(rows)] + ['link']
        msgs = []
        for row in rows:
            values = [col.text for col in row]
            values += [row.attrs['onclick'].split("'")[1]]
            msgs.append(dict(zip(headers, values)))
        self.recve = msgs
        return msgs

    def read(self, index):
        if isinstance(index, str):
            for m in self.recve:
                w = Xml(self.sess.Get(m['link']).text).select(".tab_content")[1]
                links = w.select("a")
                for a in links:
                    if index in a.text:
                        return self.sess.Get(a.attrs.get("href"))
            return
        m = self.recve[index]
        w = Xml(self.sess.Get(m['link']).text).select(".tab_content")[1]
        cprint(m, 'red')
        print(w.text)
        imgs = w.select("img")
        print("--------")
        print("Imgs:", imgs)
        links = w.select("a")
        for a in links:
            cprint(a.text + " ---> " + a.attrs.get("href",""), 'yellow')
            r = ''
            if not a.attrs.get('href'):
                continue
            while not r in ['Y','n']:
                r = input("[redirect? [Y/n]]")
                if not r:
                    r = 'n'

            if r == 'Y':
                return self.sess.Get(a.attrs.get("href"))


    def refresh(self):
        self.menu = Xml(self.sess.Get('https://10minutemail.net/').text)

    def more_10_minute(self):
        self.sess.Get('https://10minutemail.net/more.html')
        self.refresh()


    def time(self):
        return str(time.time() - self.start_time)

    def __repr__(self):
        return self.address + "|" + self.time()
        