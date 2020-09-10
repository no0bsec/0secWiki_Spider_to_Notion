## 最近想搭个类似 零组文库 的离线文档库

> 在网上找了一个gitbook的零组离线库

> 遂写个脚本把html转docx，然后传到notion上

```
# Linux安装pandoc
sudo apt install pandoc -y

# 安装python包
pip install Beautifulsoup4 lxml pypandoc

# 解压gitbook那个离线库，直接Py启动http服务
python3 -m http.server 9988

# run_script.py 修改main函数路径就可以了
if __name__ == "__main__":
    get_list('～/Desktop/easy_server')
```