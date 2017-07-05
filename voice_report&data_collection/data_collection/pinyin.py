from xpinyin import Pinyin
import time
import sqlite3


def transf(term):
    mz = sqlite3.connect(r'/python_crf/python/django/qgw/db/data_collection.db', check_same_thread=False)
    cu = mz.cursor()
    uid = time.time()
    uid = str(uid)
    term = term.replace(' ', '')
    p = Pinyin()
    termpy = p.get_pinyin(term, ' ')
    sentence = ''
    try:
        cu.execute("INSERT INTO grid (uid, terms, sentence) VALUES(?, ?, ?)", (uid, term, sentence))
    except:
        uid += 'unique'
        cu.execute("INSERT INTO grid (uid, terms, sentence) VALUES(?, ?, ?)", (uid, term, sentence))
    mz.commit()
    mz.close()
    return uid
