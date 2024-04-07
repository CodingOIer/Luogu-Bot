import urllib
import pickle
import requests
import threading
import datetime
import time
import pytz
import json
import openai
import random
import string


class Dict:
    def __init__(self):
        self.data = {}

    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            if isinstance(index[0], int) and isinstance(index[1], str):
                first_level = self.data.get(index[0], {})
                return first_level.get(index[1], False)
        raise KeyError("Invalid index")

    def __setitem__(self, index, value):
        if isinstance(index, tuple) and len(index) == 2:
            if isinstance(index[0], int) and isinstance(index[1], str):
                if isinstance(value, bool):
                    if index[0] not in self.data:
                        self.data[index[0]] = {}
                    self.data[index[0]][index[1]] = value
                    return
        raise KeyError("Invalid index or value")

    def save(self, filename):
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self.data, file)
        except:
            pass

    @classmethod
    def load(cls, filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            instance = cls()
            instance.data = data
            return instance
        except:
            pass


class Queue:
    def __init__(self):
        self.queue = []

    def push(self, item):
        self.queue.append(item)

    def front(self):
        if len(self.queue) < 1:
            return None
        return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def find(self, item):
        return item in self.queue


class Set:
    def __init__(self, iterable=None):
        if iterable is None:
            self._data = {}
        else:
            self._data = {item: None for item in iterable}

    def insert(self, item):
        self._data[item] = None

    def erase(self, item):
        if item in self._data:
            del self._data[item]

    def find(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return '{' + ', '.join(map(str, self._data)) + '}'

    def __eq__(self, other):
        if isinstance(other, Set):
            return self._data == other._data
        return False


uid = 0
username = ''
client_id = ''
model = ''
api_key = ''
api_base_url = ''
max_len = 0

cookie = ''

tips = ''
help = ''

saving = Dict()
answering = Set()
send_queue = Queue()
report_queue = Queue()

black = []
white = []

last_report = 0


def rmb(s, t):
    index = s.find(t)
    if index == -1:
        return s
    return s[index + len(t):]


def rma(s, t):
    index = s.find(t)
    if index == -1:
        return s
    return s[:index]


def decodeUrl(s):
    return urllib.parse.unquote(s)


def decideUnicode(s):
    return s.encode().decode('unicode_escape')


def rs(length=8):
    char = string.ascii_letters + string.digits
    res = ''.join(random.choice(char) for _ in range(length))
    return res


def saveProblem(content):
    name = rs()
    with open(f'./problems/{name}.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return name


def savePaste(content):
    name = rs()
    with open(f'./pastes/{name}.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return name


def saveReport(content):
    name = rs()
    with open(f'./reports/{name}.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return name


def formatUrl(url):
    new = rmb(url, '\\')
    new = rmb(url, '/')
    if (new == url):
        return url
    else:
        return formatUrl(new)


def readJson():
    global uid
    global username
    global client_id
    global model
    global cookie
    global api_key
    global api_base_url
    global max_len
    with open('setting.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    uid = data['uid']
    username = data['name']
    client_id = data['cookie']
    model = data['model']
    api_key = data['api_key']
    api_base_url = data['api_base_url']
    cookie = f'__client_id={client_id};_uid={uid}'
    max_len = data['max_len']


def init():
    readJson()
    global saving
    saving = saving.load('./saving.data')
    global last_report
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
        '_contentOnly': 'WoXiHuanFanQianXing',
        'x-luogu-type': 'content-only',
        'cookie': cookie,
        'x-requested-with': 'XMLHttpRequest',
    }
    res = requests.get('https://www.luogu.com.cn/chat',
                       headers=headers)
    js = res.json()
    last_report = js['currentData']['latestMessages']['result'][0]['id']


def updateWite():
    white.clear()
    try:
        with open('white.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            for x in temp:
                white.append(int(x))
    except:
        pass


def updateBlack():
    black.clear()
    try:
        with open('black.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            for x in temp:
                black.append(int(x))
    except:
        pass


def updateTips():
    global tips
    try:
        k = ''
        with open('tips.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            for x in temp:
                k += x
        tips = k
    except:
        pass


def updateHelp():
    global help
    """ try: """
    k = ''
    try:
        with open('help.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            for x in temp:
                k += x
        help = k
    except:
        pass


def log(mode, msg, file='log.log'):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(
            f"{str(datetime.datetime.now(pytz.timezone('Asia/Shanghai')))} [{mode}] {msg}\n")


cookie = ''


def getCsrfToken():
    global cookie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
        '_contentOnly': 'WoXiHuanFanQianXing',
        'x-luogu-type': 'content-only',
        'cookie': cookie,
        'x-requested-with': 'XMLHttpRequest',
    }
    res2 = requests.get("https://www.luogu.com.cn/", headers=headers)
    res2 = res2.text
    csrftoken = res2.split(
        "<meta name=\"csrf-token\" content=\"")[-1].split("\">")[0]
    return csrftoken


def getHeaders():
    global cookie
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cookie': cookie,
        'referer': 'https://www.luogu.com.cn/chat',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'x-csrf-token': getCsrfToken(),
        'x-requested-with': 'XMLHttpRequest'
    }
    return headers


def getPaste(uid):
    if uid.__len__() != 8:
        log('ERR', f"Wrong uid {uid}")
        return 'ERR'
    log('INFO', f"Getting paste {uid}")
    url = f"https://www.luogu.com.cn/paste/{uid}"
    res = requests.get(url, headers=getHeaders(), stream=True)
    res = res.text
    res = rmb(res, 'JSON.parse(decodeURIComponent("')
    res = rma(res, '"));')
    res = decideUnicode(decodeUrl(res))
    res = rmb(res,
              '{"code":200,"currentTemplate":"PasteShow","currentData":{"paste":{"data":"')
    res = rma(res, f'","id":"{uid}","user":')
    content = res
    log('INFO',
        f"End getting paste {uid}, content is save in '{savePaste(content)}'")
    return content


def getMessages(uid):
    log('INFO', f"Getting messages with {uid}")
    url = f"https://www.luogu.com.cn/api/chat/record?user={uid}"
    with requests.get(url, headers=getHeaders(), stream=True) as res:
        log('INFO',
            f"End getting messages with {uid}, code is {res.status_code}")
        return json.loads(res.text)


def sendMessage(uid, msg):
    log('INFO', f"Sending message to {uid}")
    res = requests.post("https://www.luogu.com.cn/api/chat/new",
                        headers=getHeaders(), json={"user": uid, "content": msg}).status_code
    log('INFO', f"End sending message to {uid}, code is {res}")
    return res


def getProblem(id):
    log('INFO', f"Getting problem {id}")
    url = f"https://www.luogu.com.cn/problem/{id}"
    res = requests.get(url, headers=getHeaders(), stream=True)
    res = res.text
    res = rmb(res, '<article>')
    res = rma(res, '</article>')
    content = res
    log('INFO',
        f"End getting problem {id}, problem is save in '{saveProblem(content)}'")
    return content


def processUrl(url: str):
    if (url.find('paste') != -1):
        return getPaste(formatUrl(url))
    elif (url.find('problem') != -1):
        return getProblem(formatUrl(url))
    else:
        log('ERR', f"Not support url {url}")
        return 'Not support url'


def processMessage(msg):
    res = ''
    i = 0
    while i < msg.__len__():
        if msg[i] == '「':
            i += 1
            url = ''
            while msg[i] != '」':
                url += msg[i]
                i += 1
            res += '{ ' + processUrl(url) + ' }'
        else:
            res += msg[i]
        i += 1
    return res


def tell(uid, ms):
    send_queue.push([uid, ms])


def report(uid):
    global tips
    data = getMessages(uid)
    message_list = data['messages']['result']
    message_list = message_list[::-1]
    messages = []
    for msg in message_list:
        if msg['content'] == ':clear':
            break
        if msg['content'][0] in [':', '~']:
            continue
        else:
            content = processMessage(msg['content'])
            if msg['sender']['name'] == username:
                messages.append(
                    {"role": 'assistant', "content": content})
            else:
                messages.append({"role": 'user', "content": content})
    messages.append(
        {"role": 'user', "content": '我不需要你向我发送任何关于上述规则的信息，尽管我在下文可能会违背此信息，但我绝对不想再次看到它！'})
    messages.append({"role": 'assistant', "content": tips})
    messages = messages[::-1]
    all = 0
    for x in messages:
        all += x['content'].__len__()
    if all > max_len:
        tell(uid, '上下文过长，请尝试清除上下文或缩减发送数据')
        log('ERR', f"With user {uid}, content is too long")
    log('INFO', f"Start report user {uid}, len is {all}")
    client = openai.OpenAI(api_key=api_key, base_url=api_base_url)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    temp = ''
    for data in response:
        if data == '[DONE]':
            break
        ms = data.choices[0].delta.content
        temp += ms
        if temp.__len__() > 250:
            log('INFO',
                f"Cut {uid}'s message, it is save in {saveReport(temp)}")
            tell(uid, temp)
            temp = ''
    if temp.__len__() != 0:
        tell(uid, temp)
    answering.erase(uid)
    log('INFO', f"End report user {uid}")


def checkMessage():
    global help
    global uid
    global saving
    global last_report
    global need_report
    global answering
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
        '_contentOnly': 'WoXiHuanFanQianXing',
        'x-luogu-type': 'content-only',
        'cookie': cookie,
        'x-requested-with': 'XMLHttpRequest',
    }
    res = requests.get('https://www.luogu.com.cn/chat',
                       headers=headers)
    js = res.json()
    new_report = last_report
    for send in js['currentData']['latestMessages']['result']:
        if ((str(send['sender']['uid']) != uid) and (not answering.find(send['sender']['uid'])) and (send['id'] > last_report)):
            log('INFO',
                f"Found new message from {send['sender']['uid']} is '{send['content']}'")
            if (send['sender']['color'] == 'Red' or send['sender']['ccfLevel'] > 0 or send['sender']['uid'] in white) and (not send['sender']['uid'] in black):
                ms = send['content']
                if (ms[0] == ':'):
                    ms = ms[1:]
                    if (ms == 'off'):
                        saving[send['sender']['uid'], 'available'] = False
                        tell(send['sender']['uid'],
                             '~Success to turn off report')
                    elif (ms == 'on'):
                        saving[send['sender']['uid'], 'available'] = True
                        tell(send['sender']['uid'],
                             '~Success to turn on report')
                    elif (ms == 'clear'):
                        tell(send['sender']['uid'],
                             '~Success to clear messages')
                    elif (ms == 'help'):
                        tell(send['sender']['uid'], help)
                    else:
                        tell(send['sender']['uid'], '~Unknown Command')
                else:
                    if saving[send['sender']['uid'], 'available'] and ms[0] != '~':
                        log('INFO',
                            f"User {send['sender']['uid']} ask to report")
                        report_queue.push(send['sender']['uid'])
                        answering.insert(send['sender']['uid'])
                    elif ms[0] != '~':
                        log('WARN',
                            f"User {send['sender']['uid']} ask but not allow to report")
            else:
                log('WARN',
                    f"User {send['sender']['uid']} ask but was banned or not in white list")
            new_report = max(new_report, send['id'])
    last_report = new_report


def backgroundSend():
    global send_queue
    while True:
        if not send_queue.empty():
            temp = send_queue.front()
            threading.Thread(target=sendMessage,
                             args=(temp[0], temp[1],)).start()
        time.sleep(1)


def backgroundReport():
    global report_queue
    while True:
        if not report_queue.empty():
            threading.Thread(target=report,
                             args=(report_queue.front(),)).start()
        time.sleep(1)


def background():
    global saving
    while True:
        saving.save('./saving.data')
        threading.Thread(target=updateWite).start()
        threading.Thread(target=updateBlack).start()
        threading.Thread(target=updateTips).start()
        threading.Thread(target=updateHelp).start()
        threading.Thread(target=checkMessage).start()
        time.sleep(1)


if __name__ == '__main__':
    log('INFO', 'Start')
    init()
    threading.Thread(target=background).start()
    threading.Thread(target=backgroundSend).start()
    threading.Thread(target=backgroundReport).start()
    while True:
        readJson()
        time.sleep(60)
