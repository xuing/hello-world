# -*- coding: UTF-8 -*-
import os
import random
import re
import time
import requests
from win32_setctime import setctime

proxy='127.0.0.1:8888'  #本地代理
proxies={
    'http':'http://'+proxy,
    'https':'https://'+proxy
}

session = requests.session()

def modifyFileTime(filename, createTime, modifyTime, accessTime,format = "%Y/%m/%d %H:%M:%S" ):
    setctime(filename, getTimeStamp(createTime,format))
    os.utime(filename, (getTimeStamp(modifyTime,format), getTimeStamp(accessTime,format)))


def getTimeStamp(mytime,format):
    return time.mktime(time.strptime(mytime, format))


def login(account,password):
    form_data = {
        'redirect': 'http://cpss.izaodao.com/study/',
        'appId': '',
        'resourceCat': '',
        'account': account,
        'password': password,
        'rand': random.random(),
        'fp': 2127634048
    }
    myRequestGet("https://passport.izaodao.com/login.do")
    response = myRequestPost("https://passport.izaodao.com/login/accountLogon.do",data=form_data)
    if response.status_code == 200:
        print("登录成功")
    else:
        input("登录失败，任意键退出")
        exit(-1)


def myRequestGet(url, num_retries=3, **kwargs):
    global html
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'Proxy-Connection': 'keep-alive'
    }
    try:
        html = session.get(url, timeout=8, headers=headers, **kwargs)
    except Exception as e:
        print('出错重试 {0}'.format(e))
        if num_retries > 0:
            return myRequestGet(url, num_retries - 1)
    return html

def myRequestPost(url, num_retries=3, **kwargs):
    global html
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'Proxy-Connection': 'keep-alive'
    }
    try:
        html = session.post(url, timeout=8, headers=headers, **kwargs)
    except Exception as e:
        print('出错重试 {0}'.format(e))
        if num_retries > 0:
            return myRequestGet(url, num_retries - 1)
    return html

def getMp4Addr(id):
    # 请求地址
    url = "http://cpssapi.izaodao.com/v/learning/getBosDownloadLink?lessonId=" + id
    # 发送get请求
    rep = myRequestGet(url)
    # print("rep"+rep.text)
    res = rep.json()
    # print(res)
    return res['data']['data'][0]
    # json.loads(rep.text)


def downloadFile(name, url):
    print("开始下载：" + name)
    # headers = {'Proxy-Connection': 'keep-alive'}
    r = myRequestGet(url, stream=True, num_retries=1)
    length = float(r.headers['content-length'])
    with open(name + '.tmp', 'wb') as f:
        count = 0
        count_tmp = 0
        time1 = time.time()
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 2:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 2
                    count_tmp = count
                    print(name + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(speed) + 'KB/S')
                    time1 = time.time()
    os.renames(name + '.tmp', name)


def formatFloat(num):
    return '{:.2f}'.format(num)


def download(file, id):
    if not os.path.exists(file):
        url = getMp4Addr(id)
        downloadFile(file, url)


def pathValid(file):
    file = file.replace(":", "：").replace("<", "《").replace(">", "》")
    rstr = r"[\/\\\*\?\"\|]"  # '/ \ : * ? " < > |'
    return re.sub(rstr, "_", file)


# 获取加入了的主修课
# http://cpssapi.izaodao.com/v/learning/getLessonBySchedule?scheduleId=
def downloadMajorById(dirPath, id):
    url = "http://cpssapi.izaodao.com/v/learning/getLessonBySchedule?scheduleId=" + id
    res = myRequestGet(url).json()
    schedules = res["data"]["data"]
    for sch in schedules:
        if sch["record_link"] == '':
            continue
        id = sch["id"]
        filename = sch["name"] + ".mp4"
        stime = sch["start_time"]
        file = dirPath + "/" + pathValid(filename)
        download(file, id)
        if stime != '':
            modifyFileTime(file, stime, stime, stime, "%Y-%m-%d %H:%M:%S")


def getMajor():
    url = "http://cpssapi.izaodao.com/v/learning/getJoinedScheduleByMajor"
    basePath = input("请输入下载路径，直接回车默认在当前路径下创建早道文件夹\r\n")
    basePath.replace('\\','/')
    if basePath.strip() == '':
        basePath = "早道/"
    if basePath[-1] != '/':
        basePath = basePath + '/'
    # 发送get请求
    # myRequestGet("http://cpss.izaodao.com/study/#/myCourse")
    rep = myRequestGet(url)
    if rep.status_code != 200:
        print(str(rep.status_code)+rep.text)
        input("连接出错，任意键退出")
    res = rep.json()
    majorList = res["data"]["data"]
    for i, major in enumerate(majorList):
        name = major["name"]
        teacher = major["teacher"]
        if "主讲" not in name and "老师" not in name:
            dirName = name + "-" + "，".join(teacher)
        else:
            dirName = name
        print("序号：%s   课程名称：%s" % (i + 1, dirName))
    try:
        num = input("请输入要下载的课程序号，用逗号隔开。不输入直接回车则全部下载\r\n")
        if num.find(',') != -1:
            num = num.split(',')
        else:
            num = num.split('，')
        for i, major in enumerate(majorList):
            if num[0] == '' or num.count(str(i+1)):
                id = major["id"]
                name = major["name"]
                teacher = major["teacher"]
                if "主讲" not in name and "老师" not in name:
                    dirName = name + "-" + "，".join(teacher)
                else:
                    dirName = name
                path = basePath + pathValid(dirName)
                if not os.path.exists(path):
                    os.makedirs(path)
                print(path)
                # 开始下载
                downloadMajorById(path, id)
    except:
        print('您输入的内容不规范或程序出错')


if __name__ == "__main__":
    print("早道网校，主修课-录播批量下载工具(非官方)  lika@xuing.cn")
    print("需要您输入账号密码，进行登录，仅本地使用，不会泄露到除官网以外的任何地方。后续会开放源代码")
    account = input("请输入账号\r\n")
    password = input("请输入密码\r\n")
    login(account,password)
    getMajor()
