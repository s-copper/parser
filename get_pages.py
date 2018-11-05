import requests
from lxml import html
import re
import threading
import time
import queue


start = time.time()
s = requests.Session()
URL = 'https://timeshop.by/naruchnyye-chasy/?page={}'
page = 1


def last_page(session, link):
    request = session.get(link.format(1))
    data = request.text
    tree = html.fromstring(data)
    href_max_num = tree.xpath('.//ul[@class="pagination"]/li[11]/a/@href')
    max_num = re.search('[0-9]*$', href_max_num[0]).group()
    return int(max_num)


def load_page(session, link):
    request = session.get(link)
    return request.text


def load_html(session, link):
    request = session.get(link)
    data = request.text
    tree = html.fromstring(data)
    return tree


def watches_href():
    while True:
        try:
            data = shop_queue.get()
        except queue.Empty:
            break
        else:
            tree = load_html(s, data)
            w_list = tree.xpath('//div[@class="product-thumb"]/*/a/@href')
            all_watches_href.extend(w_list)
            print(data)
            print(threading.currentThread().getName())
            pause = time.time()
            print(pause-start)


shop_queue = queue.Queue()
num = last_page(s, URL)


def url_gen():
    for p in range(1, last_page(s, URL)+1):
        yield URL.format(p)


for i in url_gen():
    shop_queue.put(i)

all_watches_href = []

wait = []
for i in range(5):
    thread = threading.Thread(target=watches_href)
    wait.append(thread)
    thread.start()

for i in wait:
    i.join()

print(len(all_watches_href))
#
#
# w_spec = {}
# for href in all_watches_href:
#     request = s.get(href)
#     data = request.text
#     tree = html.fromstring(data)
#     w_title = tree.xpath('.//div[@id="product-info-right"]/h1[@class="product-header"]/text()')[0]
#     key_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-5"]//div/span/text()')
#     val_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-7"]//div/text()')
#     item_spec = dict(zip(key_spec, val_spec))
#     w_spec[w_title] = item_spec
#
#
# print(w_spec.get('No Name', 'sorry'))
finish = time.time()
print(finish-start)
