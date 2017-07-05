from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import codecs
import os
import itertools
import re
import time
import sqlite3
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def time_split(input_data):
    mins = r'(((\d{1,2}|(半|一刻)|(十|一|二|三|四|五|六|七|八|九)(十)*(一|二|三|四|五|六|七|八|九)*)(分)*)*)'
    hours = r'((\d{1,2}|(十|一|二|三|四|五|六|七|八|九|两)(十)*(一|二|三|四|五|六|七|八|九|两)*)(:|点过|点整|点差|点零|点左右|点钟|点))'
    date = r'((\d{4}年)*(\d{1,2}月)\d{1,2}(日|号))'
    days = r'(今天|昨天|前天|明天|后天|刚才|刚刚)'
    section = r'(\u65e9\u4e0a|\u4e2d\u5348|\u4e0b\u5348|\u508d\u665a|\u51cc\u6668|\u665a\u4e0a|\u65e9\u6668|\u4e0a\u5348|\u534a\u591c)'
    tim = date + '|' + days + '|' + section + '|' + (hours + mins)
    jud = re.search(tim, input_data)
    times = ''
    data = input_data
    while jud:
        times = times + ',' + re.search(tim, data).group()
        data = data.replace(re.search(tim, data).group(), '')
        jud = re.search(tim, data)
    times = re.sub('^,', '', times)
    now = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    y = re.search(r'\d{4}-', now).group()
    y = int(re.sub(r'-', '', y))
    m = re.search(r'-\d{1,2}-', now).group()
    m = int(re.sub(r'-', '', m))
    d = re.search(r'-\d{1,2}\s', now).group()
    d = int(re.sub(r'-', '', d))
    h = re.search(r'\d{1,2}:', now).group()
    h = re.sub(r':', '', h)
    mi = re.search(r':\d{1,2}', now).group()
    mi = re.sub(r':', '', mi)
    ye = re.search(date, times)
    da = re.search(days, times)
    se = re.search(section, times)
    hm = re.search((hours+mins), times)
    if ye:
        input_data = input_data.replace(re.search(tim, input_data).group(), '')
    if hm:
        times = re.sub(r'一刻', r'15', times)
        times = re.sub(r'一', '1', times)
        times = re.sub(r'二', '2', times)
        times = re.sub(r'三', '3', times)
        times = re.sub(r'四', '4', times)
        times = re.sub(r'五', '5', times)
        times = re.sub(r'六', '6', times)
        times = re.sub(r'七', '7', times)
        times = re.sub(r'八', '8', times)
        times = re.sub(r'九', '9', times)
        times = re.sub(r'十', '10', times)
        times = re.sub(r'零', '0', times)
        times = re.sub(r'点过|点钟|点左右|点整', r':00', times)
        times = re.sub(r'点', r':', times)
        times = re.sub(r'半', r'30', times)
        times = re.sub(r'分', '', times)
        ho = re.search(r'\d+?:', times)
        ms = re.search(r':\d+', times)
        if re.search(r':,|:$', times):
            times = re.sub(r':,', r':00,', times)
            times = re.sub(r':$', r':00', times)
        if ho:
            ho = ho.group()
            if len(ho) == 2:
                times = re.sub(r'\d+?:', ('0' + ho), times)
            if len(ho) == 4:
                times = re.sub(r'\d+?:', (ho[0]+ho[2:]), times)
            if len(ho) == 5:
                times = re.sub(r'\d+?:', (ho[0] + ho[3:]), times)
        if ms:
            ms = ms.group()
            if len(ms) == 2:
                times = re.sub(r':\d+', (ms[0] + '0' + ms[1]), times)
            if len(ms) == 4:
                times = re.sub(r':\d+', (ms[0:2]+ms[3]), times)
            if len(ms) == 5:
                times = re.sub(r':\d+', (ms[0] + ms[3:]), times)
            if len(ms) == 6:
                times = re.sub(r':\d+', (ms[0] + ms[3] + ms[5]), times)
            if len(ms) == 7:
                times = re.sub(r':\d+', (ms[0] + ms[3] + ms[6]), times)
    if da:
        times = re.sub(r'今天', str(str(y) + '年' + str(m) + '月' + str(d) + '日'), times)
        times = re.sub(r'刚才', str(str(y) + '年' + str(m) + '月' + str(d) + '日' + h + ':' + mi), times)
        times = re.sub(r'刚刚', str(str(y) + '年' + str(m) + '月' + str(d) + '日' + h + ':' + mi), times)
        times = re.sub(r'昨天', str(str(y) + '年' + str(m) + '月' + str(d - 1) + '日'), times)
        times = re.sub(r'前天', str(str(y) + '年' + str(m) + '月' + str(d - 2) + '日'), times)
        times = re.sub(r'明天', str(str(y) + '年' + str(m) + '月' + str(d + 1) + '日'), times)
        times = re.sub(r'后天', str(str(y) + '年' + str(m) + '月' + str(d + 2) + '日'), times)
    elif ('今天' or '昨天' or '前天' or '明天' or '后天' not in times) and (not ye) and ('早上' or '中午' or '下午' or '傍晚' or '凌晨' or '晚上' in times):
        times = str(str(y) + '年' + str(m) + '月' + str(d) + '日') + times
    elif '年' not in times:
	    times = str(str(y) + '年') + times
    if se and (not hm):
	    times = re.sub(r'\u65e9\u6668|\u4e0a\u5348|\u65e9\u4e0a', r'08:00', times)
	    times = re.sub(r'中午', r'12:00', times)
	    times = re.sub(r'下午', r'16:00', times)
	    times = re.sub(r'傍晚', r'20:00', times)
	    times = re.sub(r'\u665a\u4e0a|\u534a\u591c', r'22:00', times)
	    times = re.sub(r'凌晨', r'00:00', times)
    return input_data, times


def character_split(input_data, output_file):
    output_data = open(output_file, 'w', encoding="utf-8", errors='ignore')
    for word in input_data.strip():
         word = word.strip()
         if word:
            output_data.write(word + "\tB\n")
    output_data.write("\n")
    output_data.close()


def Tagging_sentence(uid):
    cmd = 'crf_test -m model_new test' + uid + '>tag' + uid
    os.chdir(r'/python_crf/python/django/seg')
    os.system(cmd)


def character_2_word(input_file, address, event):

    input_data = open(input_file, 'r', encoding="utf-8", errors='ignore')
    for line in input_data:
        a = len(line)
        if a >2:
            char_tag_pair = line.strip().split('\t')
            char1 = char_tag_pair[0]
            tag = char_tag_pair[2]
            if tag == 'B':
                address.append(char1)
            elif tag == 'M':
                address.append(char1)
            elif tag == 'E':
                address.append(char1)
            elif tag == 'S':
                address.append(char1)
            else:
                event.append(char1)
    input_data.close()
    return address, event
	
def del_time(a):
    mins = r'(((\d{1,2}|(十|一|二|三|四|五|六|七|八|九)(十)*(一|二|三|四|五|六|七|八|九)*|(半|一刻))(分)*)*)'
    hours = r'((\d{1,2}|(十|一|二|三|四|五|六|七|八|九|两)(十)*(一|二|三|四|五|六|七|八|九|两)*)(:|点过|点整|点差|点零|点左右|点钟|点))'
    date = r'((\d{4}年)*(\d{1,2}月)\d{1,2}(日|号))'
    days = r'(今天|昨天|前天|明天|后天)'
    section = r'(\u65e9\u4e0a|\u4e2d\u5348|\u4e0b\u5348|\u508d\u665a|\u51cc\u6668|\u665a\u4e0a|\u65e9\u6668|\u4e0a\u5348|\u534a\u591c)'
    tim = date + '|' + days + '|' + section + '|' + (hours + mins)
    jud = re.search(tim, a)
    times = ''
    while jud:
        times = times + '，' + re.search(tim, a).group()
        a = a.replace(re.search(tim, a).group(), '')
        jud = re.search(tim, a)
    return a

def data_split(input_data, uid):
    address = []
    event = []
    output_file = r"/python_crf/python/django/seg/test" + uid
    input_file = r"/python_crf/python/django/seg/tag" + uid
    open(output_file, "w", encoding="utf-8", errors='ignore')
    input_data = re.sub(',|，|。', '', input_data)
    input_data, t = time_split(input_data)
    character_split(input_data, output_file)
    Tagging_sentence(uid)
    address, event = character_2_word(input_file, address, event)
    os.remove(output_file)
    os.remove(input_file)
    a = "".join(itertools.chain(address))
    a = del_time(a)
    e = "".join(itertools.chain(event))
    return a, e, t

def parse_content(content):
    resultList = re.findall(r"(确认|核对|重复|复述|是否有误)(.+?)(是的|对的|是吗|吗|对吗)", content)
    result = ''
    if len(resultList)==0:
         return result
    for resultList1 in resultList:
        count = 0
        for findstr in resultList1:
            if count == 1:
                result = findstr
            count = count + 1
    return result

@csrf_exempt
def index(request):
    if request.method == 'GET':
        con = sqlite3.connect(r'/python_crf/python/django/qgw/db/voice_report.db')
        cu = con.cursor()
        input_data = request.GET['case']
        cu.execute('select uid from user_info')
        temp = cu.fetchall()
        uid = str(temp[0][0])
        address, event, times = data_split(input_data, uid)
        uid = temp[0][0] + 1
        sql = 'update user_info set uid=' + str(uid) + ' where uid=' + str(uid-1)
        cu.execute(sql)
        con.commit()
        con.close()
        d = {'Time': times, 'Address': address, 'Event': input_data}
        return JsonResponse(d, json_dumps_params={'ensure_ascii': False},)
    elif request.method == 'POST':
        try:
            con = sqlite3.connect(r'/python_crf/python/django/qgw/db/voice_report.db')
            cu = con.cursor()
            #content = request.POST['content']
            json_info = json.loads(encoding='utf8', s=request.body.decode('utf8'))
            content = json_info['content']
            input_data = parse_content(content)
            cu.execute('select uid from user_info')
            temp = cu.fetchall()
            uid = str(temp[0][0])
            if input_data:
                address, event, time = data_split(input_data, uid)
                uid = temp[0][0] + 1
                sql = 'update user_info set uid=' + str(uid) + ' where uid=' + str(uid-1)
                cu.execute(sql)
                result = {'Result': 1, 'Address': address, 'Event': event}
            else:
                result = {'Result': 0, 'Address': '', 'Event': ''}
            con.commit()
            con.close()
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False},)
        except:
            con = sqlite3.connect(r'/python_crf/python/django/qgw/db/voice_report.db')
            cu = con.cursor()
            #input_data = request.POST['case']
            json_info = json.loads(encoding='utf8', s=request.body.decode('utf8'))
            input_data = json_info['case']
            cu.execute('select uid from user_info')
            temp = cu.fetchall()
            uid = str(temp[0][0])
            address, event, time = data_split(input_data, uid)
            uid = temp[0][0] + 1
            sql = 'update user_info set uid=' + str(uid) + ' where uid=' + str(uid-1)
            cu.execute(sql)
            con.commit()
            con.close()
            detail = {'Time': time, 'Address': address, 'Event': input_data}
            return JsonResponse(detail, json_dumps_params={'ensure_ascii': False},)
