import sqlite3
import re
from xpinyin import Pinyin


def time_transf(detail):
    date = r'((\d{4}\u5e74)*(\d{1,2}\u6708)\d{1,2}(\u65e5|\u53f7))'
    year = re.search(date, detail)
    if year:
        year = year.group()
        standard = re.sub('\u5e74|\u6708', '-', year)
        standard = re.sub('\u65e5|\u53f7', '', standard)
        standard += r' 00:00:00'
        mon = re.search('-\d-', standard)
        mins = re.search('-\d ', standard)
        if mon:
            mon = mon.group()
            standard = standard[:standard.index(mon) + 1] + '0' + standard[standard.index(mon) + 1:]
        if mins:
            mins = mins.group()
            standard = standard[:standard.index(mins) + 1] + '0' + standard[standard.index(mins) + 1:]
        detail = detail.replace(year, standard)
        return detail


#根据所有字段名获得输入数据中字段名所在坐标，提取出对应字段名及内容存入字典
def location(uid, sentence):

    mz = sqlite3.connect(r'/python_crf/python/django/qgw/db/data_collection.db')
    cu = mz.cursor()
    cu.execute("SELECT terms FROM grid WHERE uid =?", (uid,))
    terms_py = cu.fetchall()
    term = terms_py[0][0].split(',')
    mz.close()
    p = Pinyin()
    sentence = re.sub(' |,|\uff0c', '', sentence)

    sentencepy = p.get_pinyin(sentence, ' ')
    sentencepy_list = []
    for ch in sentencepy.split(' '):
        try:
            if int(ch):
                for i in range(len(ch)):
                    sentencepy_list.append(ch[i])
        except:
            sentencepy_list.append(ch)
    sentencepy = re.sub(' ', '', sentencepy)

    dic = {}
    seq = []
    i = 0
    j = 0
    for word in term:
        loc = 0
        lee = 0
        wordpy = p.get_pinyin(word, '')
        if word in sentence:
            loc = sentence.index(word)
            le = len(word)
            seq.append([loc, le])
        elif wordpy in sentencepy:
            le = len(word)
            pyloc = sentencepy.index(wordpy)
            for ch in sentencepy_list:
                if lee == pyloc:
                    break
                lee += len(ch)
                loc += 1
            sentence = sentence[:loc] + word + sentence[loc + le:]
            seq.append([loc, le])
    seq.sort()
    while j < len(seq)-1:
        if (seq[j+1][0] >= seq[j][0]) and ((seq[j+1][1] + seq[j+1][0]) <= (seq[j][1] + seq[j][0])):
            seq = seq[:j + 1] + seq[j + 2:]
            j += 1
        elif (seq[j+1][0] <= seq[j][0]) and ((seq[j+1][1] + seq[j+1][0]) >= (seq[j][1] + seq[j][0])):
            seq = seq[j + 1:]
            j += 1
        else:
            j += 1

    while i < len(seq):
        if i != len(seq)-1:
            field_detail = sentence[seq[i][0]:seq[i+1][0]]
            field = field_detail[0:seq[i][1]]
            detail = field_detail[seq[i][1]:]
            if ('\u65e5\u671f' or '\u751f\u65e5') in field:
                temp = time_transf(detail)
                if temp is not None:
                    detail = temp
            dic[field] = detail
        else:
            field_detail = sentence[seq[i][0]:]
            field = field_detail[0:seq[i][1]]
            detail = field_detail[seq[i][1]:]
            if ('\u65e5\u671f' or '\u751f\u65e5') in field:
                temp = time_transf(detail)
                if temp is not None:
                    detail = temp
            dic[field] = detail
        i += 1
    return dic
