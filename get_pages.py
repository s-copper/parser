import requests
from lxml import html
import re
import threading
import time
import queue
import xlsxwriter


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
        href = shop_queue.get()
        tree = load_html(s, href)
        w_list = tree.xpath('//div[@class="product-thumb"]/*/a/@href')
        all_watches_href.extend(w_list)
        shop_queue.task_done()
        print(href)


def url_gen():
    for p in range(1, last_page(s, URL)+1):
        yield URL.format(p)


shop_queue = queue.Queue()
num = last_page(s, URL)
all_watches_href = []

for i in range(5):
    thread = threading.Thread(target=watches_href)
    thread.daemon = True
    # wait.append(thread)
    thread.start()

for i in url_gen():
    shop_queue.put(i)

shop_queue.join()

# for i in wait:
#     i.join()
print(len(all_watches_href))

all_watches_href2 = []

for i in all_watches_href:
    j = 'https://timeshop.by' + i
    all_watches_href2.append(j)


def specification():
    while not watch_queue.empty():
        href = watch_queue.get()
        tree = load_html(s, href)
        w_title = tree.xpath('.//div[@id="product-info-right"]/h1[@class="product-header"]/text()')[0]
        key_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-5"]//div/span/text()')
        val_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-7"]//div/text()')
        item_spec = dict(zip(key_spec, val_spec))
        w_spec[w_title] = item_spec
        watch_queue.task_done()
        print(w_title)


watch_queue = queue.Queue()
w_spec = {}

for i in all_watches_href2:
    watch_queue.put(i)

for i in range(5):
    thread = threading.Thread(target=specification())
    thread.daemon = True
    thread.start()

watch_queue.join()

finish = time.time()
print(finish-start)

workbook = xlsxwriter.Workbook('watch.xlsx')
worksheet = workbook.add_worksheet('test_list')

cell_format = workbook.add_format({'bold': True})
cell_format.set_text_wrap()

worksheet.write(0, 1, 'ZIKO watch')
worksheet.set_column(0, 0, 20)
worksheet.set_column(1, 0, 15)

row = 2
col = 0

for i, j in w_spec.items():
    worksheet.write(row, col, i, cell_format)
    if not j:
        row += 1
        continue
    for n, k in j.items():
        worksheet.write(row, col+1, n)
        worksheet.write(row, col+2, k)
        row += 1

workbook.close()
