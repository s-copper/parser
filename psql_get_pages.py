import requests
from lxml import html
import threading
import time
import queue
import psycopg2


start = time.time()
s = requests.Session()
URL = 'https://timeshop.by/naruchnyye-chasy'
conn = psycopg2.connect("dbname=watch_ziko user=postgres")
cur = conn.cursor()


def load_page(session, link):
    request = session.get(link)
    return request.text


def load_html(session, link):
    request = session.get(link)
    data = request.text
    tree = html.fromstring(data)
    return tree


def watches_href():
    tree = load_html(s, URL)
    w_list = tree.xpath('//div[@class="product-thumb"]/*/a/@href')
    return w_list


all_watches_href = watches_href()

all_watches_href2 = []

for i in all_watches_href:
    j = 'https://timeshop.by' + i
    all_watches_href2.append(j)


def specification():
    global id
    while not watch_queue.empty():
        href = watch_queue.get()
        tree = load_html(s, href)
        w_title = tree.xpath('.//div[@id="product-info-right"]/h1[@class="product-header"]/text()')[0]
        article = tree.xpath('.//li[@class="product-info-li main-product-sku"]/text()')[0]
        w_title = w_title.replace(article, '')
        article = article.strip()
        key_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-5"]//div/span/text()')
        val_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-7"]//div/text()')
        item_spec0 = list(zip(key_spec, val_spec))
        item_spec = []
        for i in item_spec0:
            j = ' '.join(i)
            item_spec.append(j)
        item_spec = ', '.join(item_spec)
        cur.execute("INSERT INTO wrist_watch (name, article, specifications) VALUES (%s, %s, %s);", (
            w_title, article, item_spec))
        watch_queue.task_done()


watch_queue = queue.Queue()

for i in all_watches_href2:
    watch_queue.put(i)

for i in range(5):
    thread = threading.Thread(target=specification())
    thread.daemon = True
    thread.start()

watch_queue.join()

conn.commit()
cur.close()
conn.close()
