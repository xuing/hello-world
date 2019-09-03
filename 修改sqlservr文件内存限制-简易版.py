#coding=utf-8

if __name__ == '__main__':
    print(u"修改sqlservr文件至少2G内存的限制为512MB\n")
    oldfile = open("sqlservr", "rb").read()
    open("sqlservr.bak", "wb").write(oldfile)
    print(u"生成备份文件 sqlservr.bak \n")
    if(oldfile.find("\xff\x93\x35\x77")!=-1 or oldfile.find("\x00\x94\x35\x77")!=-1):
        newfile = oldfile.replace("\xff\x93\x35\x77", "\x00\x80\x84\x1e").replace("\x00\x94\x35\x77", "\x00\x80\x84\x1e")
        open("sqlservr", "wb").write(newfile)
        print(u"替换成功\n")
    else:
        print(u"未能找到可替换的数据，如还有内存限制的问题可私信联系我解决(xuing)")
