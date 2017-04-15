# -*- coding: utf-8 -*-

import itchat, pprint, psycopg2, re, time, threading
import core

user_info = {
    # username : [bookid,bookid]
}
book_info = {
    # bookid:{
    #   user:[userid,userid],
    #   info:{
    #       all_info:str
    #       leave:str
    #       title:str
    #       can:int
    #   }
    # }
    #
}


def get_info(book_id):
    book = core.book_info(book_id)
    if book is None:
        return None
    if book_id not in book_info:
        book_info[book_id] = {
            'user': [],
            'info': book
        }
    else:
        if book_id in book_info:
            if book['can'] > 0:
                remove_book(book_id)
        book_info[book_id]['info'] = book
    return book


def remove_book(book_id):
    print 'book', book_id, 'yeah'
    for user in book_info[book_id]['user']:
        user_info[user].remove(book_id)
        k = itchat.search_friends(userName=user)
        k.send(u'您预约的 %s-%s 这本书已经可以借了哟，快去借吧，已经帮您自动取消了预约哟' %
               (book_id, book_info[book_id]['info']['title']))
    book_info[book_id]['user'] = []


def auto_check():
    while True:
        print time.ctime(), 'auto-check begin'
        for x in book_info.keys():
            get_info(x)
        print time.ctime(), 'auto-check end'
        time.sleep(60 * 60)


def search_book(user, args):
    if args.__len__() > 1:
        book_name = args[1]
        count = 10
        try:
            count = int(args[2])
        except:
            count = 10
        result = core.search_book(book_name, count)
        if result.__len__() is 0:
            return u'没有查到相关的任何书籍'
        return result
    return u'请给我书的名字好吗'


def add_listen(user, args):
    if args.__len__() > 1:
        book_id = args[1]
        if user not in user_info:
            user_info[user] = []
        if book_id in user_info[user]:
            return u'你已经预约了这本书了'
        book = get_info(book_id)
        if book is None:
            return u'没有这本书'
        if book['can'] > 0:
            return u'不用预约哟，%s 这本书现在就可以借' % book['title']
        user_info[user].append(book_id)
        book_info[book_id]['user'].append(user)
        return u'%s\n添加了哟，如果可以借了的话，就会立即通知您的' % (book['title'])
    return u'请给我书的id好吗'


def get_book_info(user, args):
    if args.__len__ > 1:
        book_id = args[1]
        book = None
        if book_id not in book_info:
            book = get_info(book_id)
            if book is None:
                return u'骗人的，没有这本书'
        book = book_info[book_id]['info']
        return [book['all_info'], book['leave']]
    return u'请给我书的id好吗'


def remove_listen(user, args):
    if args.__len__() > 1:
        book_id = args[1]
        if user not in user_info:
            user_info[user] = []
        if book_id in user_info[user]:
            user_info[user].remove(book_id)
            book_info[book_id]['user'].remove(user)
            return u'好耶，已经取消了'
        else:
            return u'您没有预约这本书呢'

    return u'请给我书的id好吗'


def show_list(user, args):
    if user in user_info and user_info[user].__len__() is not 0:
        return u'\n'.join(user_info[user])
    return u'没有任何预约信息'


def help(user, args):
    return u'我现在支持四种指令哟，预约，取消预约，查询，预约列表，帮助，' \
           u'用法就是指令名+空格+参数（如果有多本书的话用空格隔开哟），有些指令不需要参数比如帮助和预约列表\n' \
           u'不同的指令参数也不同哟\n' \
           u'预约，取消预约，查询需要书的id，' \
           u'查找需要书的名字和想要的结果数目（没有的话默认是10）\n' \
           u'举例\n' \
           u'预约 1241241211\n' \
           u'查找 机器学习 10\n' \
           u'记住不要换行哟最后\n' \
           u'还有一个问题呀，书的id是什么？\n' \
           u'就是你在图书馆网站上打开一本书的详情页的时候，' \
           u'例如http://202.114.202.207/opac/item.php?marc_no=0000712031，就是后面的那一串数字' \
           u'知道了吧'


commands = {
    u'预约': add_listen,
    u'取消预约': remove_listen,
    u'查找': search_book,
    u'查询': get_book_info,
    u'预约列表': show_list,
    u'帮助': help
}
num_re = re.compile('[0-9]{10}')


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    user_id = msg.fromUserName
    text = msg.text
    args = text.split()
    print args, user_id
    try:
        if user_id == '@c3639b13269993d6f416be6258720ea5d2dbd8e7831193a6dcecf0135d81023a':
            if args[0] == u'上架':
                remove_book(args[1])
    except:
        pass
    if args.__len__() is not 0:
        if args[0] in commands:
            reply = commands[args[0]](user_id, args)
            if type(reply) is unicode:
                msg.user.send(reply)
            else:
                msg.user.send('\n'.join(reply))
        else:
            msg.user.send(u'{0} 这是个什么指令呀，我不懂呀'.format(args[0]))
    else:
        msg.user.send(u'你输入了什么呀，风太大我看不懂')


def has_book(bookid):
    res = get_book_info(bookid)
    return res is not None


itchat.auto_login(enableCmdQR=-1, hotReload=True)
threading._start_new_thread(auto_check, ())
itchat.run()
