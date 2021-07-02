import os
import sys

ignore_bundles = [
    'YYUDemo.bundle',
    'com.baidu.idl.face.model.bundle',
    'PASSBiometricsFaceKit.bundle',
    'PassportKit.bundle'
]

red=31
green=32
yellow=33
def print_color(text,color=green):
    print('\033[{}m{}\033[0m'.format(str(color),text))


def analyze_source(path,read=False):
    # name = path.split('/').replace('.app','')
    # path = os.path.join(name)
    os.chdir(path)
    print_color(path)
    r = os.popen('ls -l')
    contents = r.readlines()
    size = 0
    try:
        for line in contents:
            name = line.replace('\n','').split(' ')[-1]
            if read == False and 'bundle' not in name:
                continue
            if name in ignore_bundles:
                continue
            subpath = os.path.join(path,name)
            if os.path.exists(subpath) == False:
                continue
            if read == False:
                size += analyze_source(subpath,True)
            else:
                s = os.path.getsize(subpath)
                size += s
    except Exception as e:
        print(e)
    print_color('{}'.format(str(size)),yellow)
    return size

if __name__ == '__main__':
    path = sys.argv[1]
    size = analyze_source(path)
    print('\n')
    print_color('********************',red)
    print_color('totalSize : {}'.format(str(size/1024.0)),yellow)
    print_color('********************',red)
    