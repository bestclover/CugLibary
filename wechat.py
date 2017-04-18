# -*- coding: utf-8 -*-

import itchat, re, time, threading
import core, json

"""
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
"""


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
        k = itchat.search_friends(wechatAccount=user)
        if type(k) is list:
            k=k[0]
        k.send(u'您预约的 %s-%s 这本书已经可以借了哟，快去借吧，已经帮您自动取消了预约哟' %
               (book_id, book_info[book_id]['info']['title']))
    book_info[book_id]['user'] = []


def auto_check():
    while True:
        save_info()
        print time.ctime(), 'auto-check begin'
        for x in book_info.keys():
            if book_info[x]['user'].__len__() != 0:
                get_info(x)
        print time.ctime(), 'auto-check end'
        time.sleep(60 * 60)


def save_info():
    f = open('user.json', 'w+')
    f.write(json.dumps(user_info))
    f.flush()
    f.close()
    f = open('book.json', 'w+')
    f.write(json.dumps(book_info))
    f.flush()
    f.close()


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
        for i in range(1, args.__len__()):
            book_id = args[i]
            if user not in user_info:
                user_info[user] = []
            if book_id in user_info[user]:
                yield u'你已经预约了 %s-%s 这本书了' % (book_id, book_info[book_id]['info']['title'])
                continue
            book = get_info(book_id)
            if book is None:
                yield u'没有 %s 这本书' % book_id
                continue
            if book['can'] > 0:
                yield u'不用预约哟，%s 这本书现在就可以借' % book['title']
                continue
            user_info[user].append(book_id)
            book_info[book_id]['user'].append(user)
            yield u'%s\n添加了哟，如果可以借了的话，就会立即通知您的' % (book['title'])
    else:
        yield u'请给我书的id好吗'


def get_book_info(user, args):
    if args.__len__ > 1:
        book_id = args[1]
        book = None
        if book_id not in book_info:
            book = get_info(book_id)
            if book is None:
                return u'骗人的，没有这本书'
        book = book_info[book_id]['info']
        return [book['all_info'], u'可借' if book['can'] > 0 else u'不可借']
    return u'请给我书的id好吗'


def remove_listen(user, args):
    if args.__len__() <= 1:
        yield u'请给我书的id好吗'
    else:
        for i in range(1, args.__len__()):
            book_id = args[i]
            if user not in user_info:
                user_info[user] = []
            if book_id in user_info[user]:
                user_info[user].remove(book_id)
                book_info[book_id]['user'].remove(user)
                yield u'好耶，已经取消 %s-%s 的预约了' % (book_id, book_info[book_id]['info']['title'])
                continue
            else:
                yield u'您没有预约 %s 这本书呢' % book_id
                continue


def show_list(user, args):
    result = []
    if user in user_info and user_info[user].__len__() is not 0:
        for book_id in user_info[user]:
            result.append('%s %s' % (book_id, book_info[book_id]['info']['title']))
        return result
    return u'没有任何预约信息'


def help(user, args):
    return help_info


commands = {
    u'预约': add_listen,
    u'取消预约': remove_listen,
    u'查找': search_book,
    u'查询': get_book_info,
    u'预约列表': show_list,
    u'帮助': help
}
num_re = re.compile('[0-9]{10}')


@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send(help())


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def group_reply(msg):
    if msg.isAt:
        print msg
        user_id = itchat.search_friends(userName=msg.ActualNickName).alias
        text = msg.text
        args = text.split()
        msg.user.send(u'@%s\n%s' % (
            msg.actualNickName, all_reply(user_id, args[1:])))


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    user_id = msg.user.alias
    print msg
    print msg.fromUserName
    print msg.self.username
    text = msg.text
    args = text.split()
    print msg
    print args
    msg.user.send(all_reply(user_id, args))


def all_reply(user_id, args):
    print user_id,args
    try:
        if args[0] == u'记得保存信息哟':
            save_info()
            return u'还用你提醒吗？'
    except:
        pass
    if args.__len__() is not 0:
        if args[0] in commands:
            reply = commands[args[0]](user_id, args)
            if type(reply) is unicode:
                return reply
            else:
                return '\n'.join(reply)
        else:
            return u'{0} 这是个什么指令呀，我不懂呀'.format(args[0])
    else:
        return u'你输入了什么呀，风太大我看不懂'


def has_book(bookid):
    res = get_book_info(bookid)
    return res is not None


user_info = book_info = help_info = None
try:
    f = open('user.json', 'r+')
    user_info = json.loads(f.read())
    f.flush()
    f.close()
    f = open('book.json', 'r+')
    book_info = json.loads(f.read())
    f.flush()
    f.close()
    f = open('README.txt', 'r')
    help_info = f.read().decode('utf-8')
    f.flush()
    f.close()
except:
    pass
itchat.auto_login(enableCmdQR=-1, hotReload=True)
threading._start_new_thread(auto_check, ())
itchat.run()
