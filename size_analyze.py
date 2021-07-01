
#_*_coding:utf-8_*_ 
import sys
import os
import re

#简陋地计算ipa大小
#依赖python2.x 
#用法python2 size_analyze.py linkmap(linkmap完整路径)
red=31
green=32
yellow=33
def print_color(text,color=red):
    print('\033[{}m{}\033[0m'.format(str(color),text))

linkmap = None

#单个文件类
class File(object):
    name=''
    size=0
    seNum=0
    obj=None
    def __init__(self, name,seNum,obj,size=0):
        self.name = name
        self.size = size
        self.seNum = seNum
        self.obj = obj
    
#.o可执行文件
class ObjectFile(object):
    name = ''
    files=[]#记录所有文件
    _total_size=0
    def __init__(self,name, files):
        self.name = name
        self.files = files
        
    
    def total_size(self):
        size = 0
        for f in self.files:
            size += f.size
        self._total_size = size
        return self._total_size / 1024.0

class LinkMap(object):
    obj_files=[]#ObjectFile
    def __init__(self, obj_files):
        self.obj_files = obj_files
        
def get_file_line(contents):
    index=0
    file_lines=[]
    size_lines=[]
    for i in range(len(contents)):
        index = i
        line = contents[i]
        if '# Sections:' in line:
            break
        if '/opt/data/' in line:
            file_lines.append(line)

    start=False
    for i in range(index,len(contents)):
        line = contents[i]
        if 'Dead Stripped Symbols' in line:
            break
        if '# Symbols:' in line:
            start=True
            continue
        if start == False or '# Address	Size' in line:
            continue
        size_lines.append(line)
    return (file_lines,size_lines)  

def analyze():
    path = sys.argv[-1]
    if path == None:
        print_color('请输入linkmap文件路径')
        return
    contents = []
    with open(path,'r') as f:
        contents = f.readlines()
    if len(contents) == 0:
        print_color('linkmap文件为空')
        return

    files = {}
    
    #match()
    match1 = re.compile(r'[(](.*?)[)]', re.S)
    #math[]
    match2 = re.compile(r'\[([^\[\]]+)\]', re.S)

    file_lines,size_lines = get_file_line(contents)
    #分析 每个文件的序号
    for line in file_lines:
        arr = re.findall(match2,line)
        if len(arr) > 0:
            number = arr[0].replace(' ','').replace(' ','')
        part = line.split('/')[-1]
        if part == '' or part == None or '.o)' not in part:
            continue
        part = part.replace('\n','')
        obj = part.split('(')[0].replace('.a','')
        try:
            fileName = re.findall(match1,part)[0].replace('.o','').replace('.a','')
            f = File(fileName,number,obj=obj)
            files[number] = f
        except Exception as e:
            print(line)
            print(e)

    #计算每个序号对应文件的大小
    for line in size_lines:

        if line.startswith('0x') == False:
            continue

        numStrs = re.findall(match2,line)
        if len(numStrs) == 0:
            continue
        fileNum = numStrs[0].replace(' ','').replace(' ','').replace('\t','')
        
        if fileNum not in files.keys():
            # print('{} not in files'.format(fileNum))
            continue

        arr = line.split('\t')

        if len(arr) != 3:
            continue
        try:
            s = arr[1]
            if s == '' or s == ' ':
                continue
            # print('fileNum = {} size = {}'.format(fileNum,s))

            size = files[fileNum].size
            size += int(s,16)
            files[fileNum].size = size
        except Exception as e:
            print(arr)
            print(e)
        
    obj_files = {}

    #计算每个.a 文件的大小
    
    for key,f in files.items():
        if f.obj not in obj_files.keys():
            obj_files[f.obj] = ObjectFile(f.obj,[])
        
        fs = obj_files[f.obj].files
        fs.append(f)
        obj_files[f.obj].files = fs
    print('写入文件')

    
    with open('size.md','w+') as f:
        txt = ''
        total = 0
        f.write('| 包名(.a) | 大小(KB) |')
        f.write('\n')
        f.write('| :------: | :------: |')
        f.write('\n')
        for key,obj_file in obj_files.items():
            size = obj_file.total_size()
            total += size
            txt = '| {} | {} |'.format(obj_file.name,str(size))
            f.write(txt)
            f.write('\n')
        txt = '| {} | {} |'.format('total',str(total))
        f.write(txt)
if __name__ == '__main__':
    if sys.argv[-1] == '-h':
        print_color('用法：python2 size_analyze.py linkmap(linkmap完整路径)',green)
    else:
        analyze()

    

    
        