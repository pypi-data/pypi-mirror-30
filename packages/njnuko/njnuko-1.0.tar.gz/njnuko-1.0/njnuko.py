import os
import os.path
import shutil
import time
import datetime
import stat
from PIL import Image
from PIL.ExifTags import TAGS
import csv


def anf(folder,dest):
    seq = 1
    dict = {}
    log = dest + '\\' + 'list.log'
    out = open(log,'a')
    wt = csv.writer(out)    
    for i in os.listdir(folder):
            dict[seq] = i
            wt.writerow([seq,dict[seq]])
            seq = seq + 1
    out.close()
    return dict

def bijiao(folder,dict,dest):
    log = dest + '\\' +  'compare.log'
    c = []
    for i in dict:
        a = Image.open(folder  + '\\'  + dict[i])
        for j in dict:
            if i != j:
                b = Image.open(folder + '\\' + dict[j])
                try:
                    diff = ImageChops.difference(a,b)
                    if diff.getbbox() is None:
                        yuan = folder + '\\' + dict[j]
                        yuan1 = folder + '\\' + dict[i]
                        if not (yuan in c or yuan1 in c):
                            c.append(yuan)
                except ValueError as e:
                    print(e)
                    
    out = open(log,'a')
    wt = csv.writer(out)
    for k in c:
        wt.writerow([k])
        shutil.move(k,dest+ '\\'+os.path.split(k)[-1])
    out.close()
    

                
        
def compare_image(folder,dest):
    a = anf(folder,dest)
    b = bijiao(folder,a,dest)

    

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
