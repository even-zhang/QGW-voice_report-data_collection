#!/usr/bin/python3
# -*- coding:utf8 -*-
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from data_collection import pinyin
from django.views.decorators.csrf import csrf_exempt
from data_collection import segment
import json


@csrf_exempt
def terms(request):
    #term = request.POST['terms']
    json_info = json.loads(encoding='utf8', s=request.body.decode('utf8'))
    term = json_info['terms']
    uid = pinyin.transf(term)
    return JsonResponse({'uid': uid})


def index(request):
    return render(request, 'form.html')

@csrf_exempt
def seg(request):
    #uid = request.POST['uid']
    #sentence = request.POST['sentence']
    json_info = json.loads(encoding='utf8', s=request.body.decode('utf8'))
    uid = json_info['uid']
    sentence = json_info['sentence']
    if uid != '' and sentence != '':
        dic = segment.location(uid, sentence)
        return JsonResponse(dic, json_dumps_params={'ensure_ascii': False}, )
    else:
        return  HttpResponse('Please Input uid and sentence')
