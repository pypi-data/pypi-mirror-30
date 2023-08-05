import os
import os.path
import shutil
import time
import datetime
import stat
from PIL import Image,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import ImageChops

from PIL.ExifTags import TAGS


import csv


def anf(folder,dest):
    seq = 1
    dict = {}
    log = os.path.join(dest,'list.log')
    out = open(log,'a')
    wt = csv.writer(out)    
    for i in os.listdir(folder):
            dict[seq] = i
            wt.writerow([seq,dict[seq]])
            seq = seq + 1
    out.close()
    return dict

def bijiao(folder,dict,dest):
    log = os.path.join(dest,'compare.log')
    c = []
    for i in dict:


        try:
            print('versify the image')
            Image.open(os.path.join(folder,dict[i]))
        except IOError:
            print("IO ERROR" + r'Image.open(os.path.join(folder,dict[i]))')
            continue
        a = Image.open(os.path.join(folder,dict[i]))
        a1 = os.path.getsize(os.path.join(folder,dict[i]))
        print("a1="+ str(a1))
        for j in dict:
            if j != i:
                b1 = os.path.getsize(os.path.join(folder,dict[j]))
                print("b1="+ str(b1))
                if a1 == b1:
                    try:        
                        Image.open(os.path.join(folder,dict[j]))
                    except IOError:
                        print("IO ERROR" + r'Image.open(os.path.join(folder,dict[j]))')
                        continue
                    b = Image.open(os.path.join(folder,dict[j]))
                    try:
                        diff = ImageChops.difference(a,b)
                        if diff.getbbox() is None:
                            yuan = os.path.join(folder,dict[j])
                            yuan1 = os.path.join(folder,dict[i])
                            if not (yuan in c or yuan1 in c):
                                c.append(yuan)
                    except ValueError as e:
                        print(e)
                    
    out = open(log,'a')
    wt = csv.writer(out)
    for k in c:
        wt.writerow([k])
        shutil.move(k,os.path.join(dest,os.path.split(k)[-1]))
    out.close()
    

                
        
def compare_image(folder,dest):
    a = anf(folder,dest)
    b = bijiao(folder,a,dest)

    

def file_move(frfolder,file1,type,dest,file2):
    log = os.path.join(dest,'process.log')

    if os.path.exists(os.path.join(dest,type,file2,type)):
        file_move(frfolder,file1,type,dest,file2+'-1')
    else:
        if type != 'no':
            shutil.move(os.path.join(frfolder,file1 + '.' + type),os.path.join(dest,type,file2 + '.' + type))
            out = open(log,'a')
            wt = csv.writer(out)            
            wt.writerow([os.path.join(frfolder,file1 + '.'+ type),os.path.join(dest,type,file2 + '.' + type)])
            out.close()
        else:
            shutil.move(os.path.join(frfolder,file1),os.path.join(dest,type,file2))
            out = open(log,'a')
            wt = csv.writer(out)            
            wt.writerow([os.path.join(frfolder,file1 + '.'+ type),os.path.join(dest,type,file2 + '.' + type)])
            out.close()
            
def class_files(folder,dstfold):
       
    for i in os.listdir(folder):
        if os.path.isdir(os.path.join(folder,i)):
            class_files(os.path.join(folder,i),dstfold)
        else:
            if i.find('.') > 0:
                type = i.split(".")[-1]
                file_name = i[0:i.rindex('.')]
                if not (os.path.exists(os.path.join(dstfold,type)) and not os.path.isfile(os.path.join(dstfold,type))):
                    os.makedirs(os.path.join(dstfold,type))
                file_move(folder,file_name,type,dstfold,file_name)

            else:
                type = 'no'
                file_name = i
                if not (os.path.exists(os.path.join(dstfold,type)) and not os.path.isfile(os.path.join(dstfold,type))):
                    os.makedirs(os.path.join(dstfold,type))
                file_move(folder,file_name,type,dstfold,file_name)
def main():
    pass

if __name__ == '__main__':
    main()
