#!/public/home/jcli/public/bin/python3
#-*-coding=utf-8 -*-
##############################################################################
#                  author     zhangkun                                       #
#                  email      tianguolangzi@gmail.com                        #
#                  V          2.0                                            #
#                  date       2016-11-28                                      #
##############################################################################

#update
#2017-11-27  简化参数

import os,sys,re,gzip
import time
import argparse
from collections import defaultdict

__version__=2.0

def purpose():
    print('''这是一个脚本,从第一个文件中取某一列作为键,在第二个文件中某一列出现该键,则合并两个文件中的这两行,多进程读入文件,多进程写入文件''')
    sys.exit()

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action = 'version', version = 'K2K.py {}'.format(__version__))
    parser.add_argument('files', nargs = '*', help = '可以接多个参数' )
    parser.add_argument('--header',nargs = '*',help = '是否存在文件头,1 yes ,0 no')
    parser.add_argument('--K1',nargs = '*',help = '文件1中选做key的列')
    parser.add_argument('--K2',nargs = '*',help = '文件2中选做key的列')
    parser.add_argument('--O1',nargs = '*',help = '文件1中要输出的列')
    parser.add_argument('--O2',nargs = '*',help = '文件2中要输出的列')
    parser.add_argument('--do',choices=['U','I','A'],default='I',help="A, 只取第二个文件中的键, U取两文件并集, I,只取交集")
    parser.add_argument('-r','--Replace',default="_#_",help="UnionOrIntersect 为 A时,第二个文件空缺的部分由'_#_'填充")
    parser.add_argument('-d', default = '\t', help = '指定分隔符')
    parser.add_argument('-o',"--out", default = 'K2K.tmp', help = '输出文件')
    return parser

def readfile(H,File,KeyIndex,OF,OutIndex,Replace):
    print('读入文件:',File,H,KeyIndex,OutIndex)
    print('有文件头:','Y' if H else 'N')
    print('分隔符:',OF)
    print('作键的列:',"\t".join([str(i+1) for i in KeyIndex ]))
    print('输出的列:',"\t".join([str(i+1) for i in OutIndex ]))
    
    
    A1=gzip.open(File,"rt") if File[-3:] == '.gz' else open(File,"r")
    KeyDict=defaultdict(lambda:"\t".join([Replace]*len(OutIndex)))
    lines=A1.readlines()[1:] if H else   A1.readlines()
    for line in lines:
        if "#" ==line[0]:continue
        if line=='\n':continue
        tmp=line.strip().split(OF)
        #print(tmp)
        Key=[]
        for Index in KeyIndex:
            Key.append(tmp[Index])
        Key="\t".join(Key)
        con=[]
        for Index in OutIndex:
            #print(Index)
            con.append(tmp[Index])
        KeyDict[Key]="\t".join(con)
    A1.close()
    return KeyDict

def writefile(File):
    A2=gzip.open(File) if File[-3:] == '.gz' else open(File)
    A2.close()

def get_index_list(Index):
    tmp=[]
    tmp1=[]
    tmp2=[]
    for i in Index:
        tmp.extend(i.split(","))
    tmp1= [i for i in tmp if i not in tmp1]
    if "" in tmp1: tmp1.remove("")
    for i in tmp1:
        if i =="":continue
        if "-" not in i :
            tmp2.append(int(i)-1)
        else:
            l,m=list(map(int,i.split("-")))
            for j in range(l,m+1):
                tmp2.append(j-1)
    #print(tmp2)
    return tmp2


def K2K(Header,File1,File2,KeyIndex1,KeyIndex2,OutIndex1,OutIndex2,Replace,OF,UnionOrIntersect):
    
    KeyDict1=readfile(Header[0],File1,KeyIndex1,OF,OutIndex1,Replace)
    KeyDict2=readfile(Header[1],File2,KeyIndex2,OF,OutIndex2,Replace)
    keyset1=set(KeyDict1.keys())
    keyset2=set(KeyDict2.keys())
    if UnionOrIntersect =='U':
        keyset=keyset2 | keyset1
        #两文件的并集
    elif UnionOrIntersect =='I':
        keyset=keyset2 & keyset1
        #两文件的交集
    elif UnionOrIntersect == 'A':
        keyset=keyset2
        #只要存在file2中的
    return keyset,KeyDict1,KeyDict2

    #with open(OutFile,'wt') as A2:
    #   A1=gzip.open(File1,"rt") if File1[-3:] == '.gz' else open(File1,'r')
    #   for line in A1.readlines():
    #       tmp=line.strip().split(OF)
    #       Key=[]
    #       for Index in KeyIndex1:
    #           #print(Index)
    #           Key.append(tmp[Index])
    #       Key="_".join(Key)
    #       con=[]
    #       for Index in OutIndex1:
    #           con.append(tmp[Index])
    #       con="\t".join(con)
    #       if Key in KeyDict:
    #           con+= "\t"+KeyDict[Key]
    #       else:
    #           if UnionOrIntersect == 'A':
    #               con+= "\t"+"\t".join(["_#_"]*len(OutIndex2))
    #           else:
    #               continue
    #       A2.write("{}\t{}\n".format(Key.replace("_","\t"),con))

def main():
    parser = get_parser()
    args = parser.parse_args()
    if len(args.files) <=1:
        purpose()
    File1,File2=args.files[:2]
    OF=args.d
    OutFile=args.out
    if args.header is None:args.header='0,0'
    Header=get_index_list(args.header)
    Header=[h+1 for h in Header]
    KeyIndex1=get_index_list(args.K1)
    KeyIndex2=get_index_list(args.K2)
    OutIndex1=get_index_list(args.O1)
    OutIndex2=get_index_list(args.O2)
    UnionOrIntersect=args.do
    Replace  =args.Replace
    keyset,KeyDict1,KeyDict2=K2K(Header,File1,File2,KeyIndex1,KeyIndex2,OutIndex1,OutIndex2,Replace,OF,UnionOrIntersect)
    with open(OutFile,'wt') as A2:
        for k in sorted(keyset):
            A2.write("{}\t{}\t{}\n".format(k,KeyDict1[k],KeyDict2[k]))
    
if __name__ == '__main__':
    main()




