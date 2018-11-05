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
    global num
    while num >= 1:
        data = URL.format(num)
        tree = load_html(s, data)
        w_list = tree.xpath('//div[@class="product-thumb"]/*/a/@href')
        all_watches_href.extend(w_list)
        num -= 1
        print(num)
        print(threading.currentThread().getName())


shop_queue = queue.Queue()
num = last_page(s, URL)


# def put_queue(url):
#     global num
#     while num >= 1:
#         shop_queue.put(url)
#         num -= 1
#
#
# for i in range(5):
#     lite_thread = threading.Thread(target=put_queue, args=URL.format(num))
#     lite_thread.daemon = True
#     lite_thread.start()
# for i in range(1, last_page(s, URL)+1):
#     shop_queue.put(URL.format(i))
# shop_queue.join()


all_watches_href = []

waitfor = []
for i in range(5):
    thread = threading.Thread(target=watches_href)
    waitfor.append(thread)
    thread.start()

for i in waitfor:
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
