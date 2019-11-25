import os
import re

## initialize these variables

dir2=r"E:\data1\dat2\docs"




regex2=r"ff_sid_adm.pl.*syb.*"


##

print("directory name is", dir2)

filelist=[]

def get_files_in_a_directory(dir1):
    global filelist
    if os.path.isdir(dir1):
        listlevel1=os.listdir(dir1)
        if (len(listlevel1)==0):
            #print("no files found in", dir1)
            return
        else:
            for i in listlevel1:
                if os.path.isfile(dir1+'\\'+i):
                    filelist.append(dir1+'\\'+i)
                elif os.path.isdir(dir1+'\\'+i):
                    get_files_in_a_directory(dir1+'\\'+i)
    else:
        print(dir1,"is NOT a directory.")

## function 2
def check_pattern_in_file(file1, regex1):
    fin = open(file1, 'rt', encoding="ISO-8859-1")
    occurence = 0
    while True:
        line=fin.readline()
        if not line:
            break
        m = re.search(regex1,line,re.IGNORECASE)
        if m:
            if (occurence==0):
                print(file1)
                occurence+=1
            print(line)
    fin.close()
##

## main
get_files_in_a_directory(dir2)


for i in filelist:
    check_pattern_in_file(i, regex2)

