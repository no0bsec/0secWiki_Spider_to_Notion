#!/usr/bin/env python3
# -*- coding:utf-8 -*-

##########################################################################
#              根据零组对外的json目录数据，提取文章ID去爬取文章数据              #
#                cookie过期时间2小时，以后再写自动登录取cookie                 #
#    估计零组服务器写了逻辑抓取用户访问频率，所以为了模拟真人操作，建议每小时爬5章     #
#                  毕竟正常人不会每小时不间断请求，即便做了延时                  #
#                 因近日零组已关闭了文库，so，脚本也没啥用了                  #
##########################################################################


import os
import time
import re
import random
import requests
import pypandoc
from pathlib import Path
from Secrets import SECRETS


file_location = os.getcwd()+"/"
try:
    os.remove(file_location+"history.log")  # 开启脚本首先删除下载历史记录
    os.remove(file_location+"__pycache__")
except:
    pass

# with open('../json_data/json_data.json', 'r') as f:
#     a = f.read()
# json_data = (eval(a))['data']

doc_reduce_total = 0


# 递减文章数
def recursion_reduce(doc_num):
    global doc_reduce_total
    doc_reduce_total = doc_num - 1


def document_spider(location, doc_id, doc_name):
    docu_url = "https://wiki.0-sec.org/api/wiki/articleInfo/"
    img_url = "https://wiki.0-sec.org"

    logged_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'Zero-Token=' + SECRETS['keys']['Zero-Token'],
        'referer': 'https://wiki.0-sec.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Zero-Token': SECRETS['keys']['Zero-Token']
    }
    url = docu_url + str(doc_id)
    try:
        req = requests.get(url, headers=logged_headers)
    except:
        time.sleep(65)  # 有时服务器会断开请求，但cookie在2小时内有效，延时一分多钟继续爬
        req = requests.get(url, headers=logged_headers)

    # print(req.json())
    document_data = req.json()

    try:
        document_data['data']
    except:
        print(">>> 零组Cookie过期，程序退出！ <<<")
        exit(0)

    html_file = doc_name + ".html"
    if not re.search("https://wiki.0-sec.org/img", document_data['data']):
        clean_data = re.sub(r'/img', img_url + "/img", document_data['data'])  # 将html中的img路径补全
    else:
        clean_data = document_data['data']
    # print(clean_data)
    html_file = re.sub(r'/', "_", html_file)
    with open(location + html_file, "w") as f:
        f.write(clean_data)
    pypandoc.convert_file(location + html_file, 'docx', outputfile=location + html_file[:-5] + ".docx")
    print("docx文件转换完成！", "\n")
    # os.remove(location + "/" + html_file)
    # print("删除html文件了？！")
    return "docx文件转换完成！"


# 抓取json目录
def query_json_catalog():
    json_url = "https://wiki.0-sec.org/api/wiki/tree"  # 零组对外的json目录数据
    json_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    }

    req = requests.get(json_url, headers=json_headers)
    # print(req.json())
    json_data = req.json()
    return json_data


doc_total = []


# 递归取剩余文章数
def recursion_doc(json_data, location):
    for i in range(0, len(json_data)):
        if json_data[i]['name'] == '友情链接':
            continue
        if json_data[i]['treeNode']:
            tmp_location = clean_folder_name(location, json_data[i]['name'])
            recursion_doc(json_data[i]['treeNode'], tmp_location)  # 把目录树 和 路径递归到下一次
        else:
            doc_name = re.sub(r'/', "_", json_data[i]['name'])
            docx_file_path = "{}{}.docx".format(location, doc_name)
            if not Path(docx_file_path).is_file():
                doc_total.append(json_data[i]['name'])


# 保存下载历史记录
def save_down_log(file_path):
    with open("./history.log", "a") as history_data:
        history_data.writelines(file_path+'\n')


# 校验本地是否存在爬过的文件
def check_doc_exists(location, doc_name):
    doc_name = re.sub(r'/', "_", doc_name)
    docx_file_path = "{}{}.docx".format(location, doc_name)
    if Path(docx_file_path).is_file():
        print("已下载--> ", doc_name+".docx", "\n")
        return False
    else:
        return True


# 清洗目录中带有 / 的不合法文件名
def clean_folder_name(location, data):
    data = re.sub(r'/', "_", data)
    tmp_location = location + data + "/"

    if not Path(location + data + "/").is_dir():
        os.mkdir(location + data + "/")  # 创建目录
    return tmp_location


# 爬取文章计数
end_list = []


# 递归json目录树数据
def recursion_function(json_data, location=None):
    for i in range(0, len(json_data)):
        if json_data[i]['name'] == '友情链接':
            continue
        if json_data[i]['treeNode']:
            # print("目录： ", json_data[i]['name'])
            tmp_location = clean_folder_name(location, json_data[i]['name'])
            recursion_function(json_data[i]['treeNode'], tmp_location)  # 把目录树 和 路径递归到下一次
        else:
            if check_doc_exists(location, json_data[i]['name']):
                if len(end_list) == 5:
                    print(">>> 当前已爬5篇文章，为避免触发零组爬虫审查封号机制，程序退出！ <<<")
                    exit(0)
                print("剩余待爬文章总数： ", str(doc_reduce_total))
                print("正在等待延时下载： ", json_data[i]['name'])

                doc_id, doc_name = json_data[i]['id'], json_data[i]['name']
                time.sleep(random.randint(70, 90))
                document_spider(location, doc_id, doc_name)  # 启动爬虫
                save_down_log(location+json_data[i]['name']+".docx")
                end_list.append(location+json_data[i]['name'])
                recursion_reduce(doc_reduce_total)


if __name__ == '__main__':
    json_data = query_json_catalog()
    json_data = json_data['data']
    recursion_doc(json_data, file_location)
    doc_reduce_total = len(doc_total)

    recursion_function(json_data, file_location)  # 递归轮询

