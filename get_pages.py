import requests
from lxml import html
import re
import threading


s = requests.Session()
URL = 'https://timeshop.by/naruchnyye-chasy/?page={}'
page = 1


def last_page(session, link):
    request = session.get(link.format(1))
    data = request.text
    tree = html.fromstring(data)
    href_max_num = tree.xpath('.//ul[@class="pagination"]/li[11]/a/@href')
    max_num = re.search('[0-9]*$', href_max_num[0]).group()
    return max_num


def load_watches(link, session):
    request = session.get(link)
    return request.text


# def contain_watches_data(text):
#     t = html.fromstring(text)
#     watch_list = t.xpath('//div[@id="res-products"]')
#     if len(watch_list) == 0:
#         return False
#     else:
#         return True
#
#
# all_watches_href = []
# while True:
#     data = load_pages(s, URL)
#     tree = html.fromstring(data)
#     if contain_watches_data(data):
#         w_list = tree.xpath('//div[@class="product-thumb"]/*/a/@href')
#         all_watches_href.extend(w_list)
#         page += 1
#     else:
#         break
#
#
# num = 1
# w_spec = {}
# for href in all_watches_href:
#     one_w_spec = []
#     text = load_watches(href, s)
#     h = html.fromstring(text)
#     w_title = h.xpath('.//ul[@class="breadcrumb"]/li[4]/*/span[@itemprop="name"]/text()')[0]
#     key_spec = h.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-5"]//div/span/text()')
#     val_spec = h.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-7"]//div/text()')
#     item_spec = dict(zip(key_spec, val_spec))
#     w_spec[w_title] = item_spec

