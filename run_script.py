#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import re
import pypandoc
from bs4 import BeautifulSoup


def rep_img_link(home, html):
    full_img_url ='src="http://0.0.0.0:9988'+home[32:]+'/img/'
    clean_data = re.sub(r'src="img/', full_img_url, html)  # 将html中的img路径补全
    return clean_data


def bs_select_title(html):
    soup = BeautifulSoup(html, 'lxml')
    select_num = str(soup)[14:15]
    # print(select_num)
    if select_num == "1":
        title_name = str(soup.h1['id'])
    elif select_num == "2":
        title_name = str(soup.h2['id'])
    elif select_num == "3":
        title_name = str(soup.h3['id'])
    else:
        title_name = str(soup.h4['id'])

    return title_name


def bs_select_html(html):
    soup = BeautifulSoup(html, 'lxml')
    clean_data = soup.find('section', class_='normal markdown-section')
    clean_data = str(clean_data)
    source_data = clean_data[42:-395]
    return source_data


def get_list(dir):
    for home, dirs, files in os.walk(dir):
        for filename in files:
            if filename[-3:] != "png" and filename[-4:] != "docx" and filename[-3:] != "gif" and filename[-3:] != "jpg" and filename[-4:] != "jpeg":
                fullname = os.path.join(home, filename)
                print("--> ", fullname)
                with open(fullname, 'r') as f:
                    source_data = bs_select_html(f.read())
                # print(source_data)
                html_title = bs_select_title(source_data)
                full_html_path = home+'/'+html_title+'.html'
                source_data = rep_img_link(home, source_data)

                with open(full_html_path, "w") as f:
                    f.write(source_data)
                pypandoc.convert_file(full_html_path, 'docx',
                                      outputfile=str(full_html_path[:-5]) + ".docx")
                print("docx文件转换完成！\n")
                try:
                    os.remove(fullname)
                    os.remove(full_html_path)
                except:
                    pass
                # exit(0)


if __name__ == "__main__":
    get_list('~/Desktop/easy_server')
