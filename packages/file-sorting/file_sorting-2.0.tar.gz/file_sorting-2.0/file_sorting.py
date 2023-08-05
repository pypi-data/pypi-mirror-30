import os
import os.path
import shutil
import time
import datetime
import stat
from PIL import Image
from PIL.ExifTags import TAGS
import csv

def file_move(frfolder,file1,type,dest,file2):
    log = dest + '\\'+'process.log'

    if os.path.exists(dest + '\\' + type + '\\' + file2 + '.' + type):
        file_move(frfolder,file1,type,dest,file2+'-1')
    else:
        shutil.move(frfolder + '\\' + file1 + '.' + type, dest + '\\' + type + '\\' + file2 + '.' + type)
        out = open(log,'a')
        wt = csv.writer(out)            
        wt.writerow([frfolder + '\\' + file1 + '.'+ type, dest + '\\' +  type +  '\\'+ file2 + '.' + type])
        out.close()
                    
def class_files(folder,dstfold):
       
    for i in os.listdir(folder):
        if os.path.isdir(os.path.join(folder,i)):
            class_files(os.path.join(folder,i),dstfold)
        else:
            type = i.split(".")[-1]
            file_name = i[0:i.rindex('.')]
            if not (os.path.exists(dstfold + '\\' + type) and not os.path.isfile(dstfold + '\\' + type)):
                os.makedirs(dstfold + '\\' + type)
            file_move(folder,file_name,type,dstfold,file_name)
def main():
    pass

if __name__ == '__main__':
    main()
