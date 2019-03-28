from lxml import html, etree
import time
import xlsxwriter
import xlrd
import asyncio
import aiohttp


start = time.time()

all_watches_url = []


workbook = xlrd.open_workbook('async_watch.xlsx')
worksheet = workbook.sheet_by_name('watches_urls_list')

_row = 1
_col = 0

while True:
    try:
        url = worksheet.cell(_row, _col).value
    except IndexError as e:
        break
    else:
        all_watches_url.append(url)
        _row += 1


async def get_specification(asession, link):
    async with asession.get(link) as response:
        data = await response.text()
        if data:
            tree = html.fromstring(data)
            task = try_get_spec(tree)
            await asyncio.gather(task)
        else:
            print(link)
            async with aiohttp.ClientSession() as asession:
                task = asyncio.ensure_future(get_specification(asession, link))
                await asyncio.gather(task)


async def try_get_spec(tree):
    try:
        w_title = tree.xpath('.//div[@id="product-info-right"]/h1[contains(@class, "product-header")]/text()')[0]
        key_spec = tree.xpath('.//div[@id="tab-specification"]//div[contains(@class, "col-xs-5")]//div/span/text()')
        val_spec = tree.xpath('.//div[@id="tab-specification"]//div[contains(@class, "col-xs-7")]//div/text()')
        item_spec = dict(zip(key_spec, val_spec))
        w_spec[w_title] = item_spec
    except Exception:
        try_get_spec(tree)


async def write_spec(l):
    tasks = []
    print('test')
    async with aiohttp.ClientSession() as asession:
        for link in l:
            task = asyncio.ensure_future(get_specification(asession, link))
            tasks.append(task)
        await asyncio.gather(*tasks)


gen_watches_url = (all_watches_url[i:i+100] for i in range(len(all_watches_url)) if i % 100 == 0)

w_spec = {}


loop = asyncio.get_event_loop()

for l in gen_watches_url:
    loop.run_until_complete(write_spec(l))

loop.close()


workbook = xlsxwriter.Workbook('async_watch.xlsx')
worksheet = workbook.add_worksheet('specification_list')

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
