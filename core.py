# -*- coding: utf-8 -*-

import requests
from scrapy import Selector

search_url = 'http://202.114.202.207/opac/openlink.php'
book_url = 'http://202.114.202.207/opac/item.php'


def search_book(book_name, count=10):
    result = []
    pagepg = min(100, count)
    for i in range((count + pagepg - 1) / pagepg):
        res = requests.get(search_url,
                           params={'strSearchType': 'title', 'strText': book_name, 'page': i + 1, 'displaypg': pagepg})
        res.encoding = 'utf-8'
        response = Selector(res)
        for x in response.xpath("//*[@class='book_list_info']"):
            name = '.'.join(x.xpath(".//a[@target='_blank']/text()").extract_first().split('.')[1:])
            id = x.xpath(".//a[@target='_blank']/@href").extract_first().split('=')[-1]
            book = int(x.xpath("./p/span/text()[2]").extract_first().split(u'：')[-1])
            result.append(u'%s %s 可借%d' % (name, id, book))
    if result.__len__() > count:
        return result[:count]
    else:
        return result


def book_info(book_id):
    if book_id.__len__() is 10:
        try:
            int(book_id)
        except:
            return None
        result = {}
        res = requests.get(book_url, params={'marc_no': book_id})
        res.encoding = 'utf-8'
        response = Selector(res)
        r = []
        for x in response.xpath("//*[@class='booklist']"):
            key = x.xpath("./dt//text()").extract_first()
            value = x.xpath("./dd//text()").extract_first()

            if key is None or value is None:
                continue
            r.append('%s%s' % (key, value))

        if r.__len__() > 0:
            result['all_info'] = '\n'.join(r)
            result['title'] = ''.join(r[0].split(":")[1:])
            info = response.xpath("//*[@id='item']//td[5]//text()").extract()
            count = 0
            for x in info:
                if x == u'可借':
                    count += 1

            result['can'] = count
            if info.__len__() > 0: result['leave'] = '\n'.join(info)
            return result
    return None


if __name__ == '__main__':
    result = search_book(u'机器', 30)
    print '\n'.join(result)
