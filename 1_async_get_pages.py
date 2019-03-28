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
    return int(max_num)


async def get_watches_url(asession, link):
    async with asession.get(link) as response:
        data = await response.text()
        try:
            tree = html.fromstring(data)
        except etree.ParserError:
            print(link)
        all_watches_urls.extend(tree.xpath('//div[@class="product-thumb"]/*/a/@href'))


async def write_list_of_watches(link):
    num = last_page(s, link)
    tasks = []
    async with aiohttp.ClientSession() as asession:
        for i in range(1, num + 1):
            task = asyncio.ensure_future(get_watches_url(asession, link.format(i)))
            tasks.append(task)
        await asyncio.gather(*tasks)


all_watches_urls = []
# a = (l[i:i+20] for i in range(len(l)) if i%20 == 0)


loop = asyncio.get_event_loop()
loop.run_until_complete(write_list_of_watches(URL))
loop.close()


print(time.time() - start)
print(len(all_watches_urls))


workbook = xlsxwriter.Workbook('async_watch.xlsx')
worksheet = workbook.add_worksheet('watches_urls_list')

cell_format = workbook.add_format({'bold': True})
cell_format.set_text_wrap()

worksheet.write(0, 1, 'ZIKO watch', cell_format)

row = 1
col = 0

for i in all_watches_urls:
    worksheet.write(row, col, i)
    row += 1


workbook.close()

print(time.time() - start)
