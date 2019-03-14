import requests
from lxml import html, etree
import re
import time
import xlsxwriter
import asyncio
import aiohttp


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
    print(max_num)
    return int(max_num)


async def get_watches_url(asession, link):
    async with asession.get(link) as response:
        data = await response.text()
        tree = html.fromstring(data)
        all_watches_url.extend(tree.xpath('//div[@class="product-thumb"]/*/a/@href'))


async def write_list_of_watches(link):
    num = last_page(s, URL)
    tasks = []
    async with aiohttp.ClientSession() as asession:
        for i in range(1, num + 1):
            task = asyncio.ensure_future(get_watches_url(asession, link.format(i)))
            tasks.append(task)
        await asyncio.gather(*tasks)


all_watches_url = []


loop = asyncio.get_event_loop()
loop.run_until_complete(write_list_of_watches(URL))
loop.close()


print(time.time() - start)
print(len(all_watches_url))


async def get_specification(asession, link):
    async with asession.get(link) as response:
        data = await response.text()
        tree = html.fromstring(data)
        w_title = tree.xpath('.//div[@id="product-info-right"]/h1[@class="product-header"]/text()')[0]
        key_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-5"]//div/span/text()')
        val_spec = tree.xpath('.//div[@id="tab-specification"]//div[@class="col-xs-7"]//div/text()')
        item_spec = dict(zip(key_spec, val_spec))
        w_spec[w_title] = item_spec


async def write_spec():
    tasks = []
    async with aiohttp.ClientSession() as asession:
        for link in all_watches_url:
            task = asyncio.ensure_future(get_specification(asession, link))
            tasks.append(task)
        await asyncio.gather(*tasks)

w_spec = {}

loop2 = asyncio.get_event_loop()
loop2.run_until_complete(write_spec())
loop2.close()


workbook = xlsxwriter.Workbook('async_watch.xlsx')
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

print(time.time() - start)
