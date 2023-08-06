import os
import os.path
import shutil
import time
import datetime
import stat
from PIL import Image,ImageFile
from PIL import ImageChops
from PIL.ExifTags import TAGS
import locale
locale.getdefaultlocale()


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
        a1 = getsize(folder,dict[i])
        print("a1="+ str(a1))
        for j in dict:
            if j != i:
                b1 = getsize(folder,dict[j])
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
            
def class_files_bytype(folder,dstfold):
       
    for i in os.listdir(folder):
        if os.path.isdir(os.path.join(folder,i)):
            class_files_bytype(os.path.join(folder,i),dstfold)
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


def rename(loc,fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    print(os.path.join(loc,fname))
    print('----------------------')
    try:
        img = Image.open(os.path.join(loc,fname))
        if hasattr( img, '_getexif' ):
            try:
                exifinfo = img._getexif()
            except:
                exifinfo = None
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
            else:
                timeArray = time.localtime(os.path.getctime(fname))
                otherStyleTime = time.strftime("%Y-%m-%d-%H%M%S", timeArray)
                return str(otherStyleTime).replace(':','-').replace(' ','_')  
    except IOError:
        print('IOERROR ' + fname)
    if ret.get('Make') != None:
        mk = ret.get('Make').replace(' ','').strip().strip('\x00')
    else:
        mk = ''
    if ret.get('DateTimeOriginal') != None:
        cd = ret.get('DateTimeOriginal')[0:10].replace(':','-').replace(' ','_') + '-' + ret.get('DateTimeOriginal')[10:].replace(':','').replace(' ','')     
    else:
        cd = ''
    if mk+cd != '':
        return '-'.join([mk,cd]).strip('-')
    else:
        timeArray = time.localtime(os.path.getctime(os.path.join(loc,fname)))
        otherStyleTime = time.strftime("%Y-%m-%d-%H%M%S", timeArray)
        return str(otherStyleTime).replace(':','-').replace(' ','_')



def gettime(loc,fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    print(fname)
    print('--------------------------------------------')
    try:
        if fname.index('.') > 0:
            e = os.path.splitext(fname)[-1]
            if e.lower() in ('.jpg','.jpeg','.gif','.png','.bmp'):    
                try:
                    img = Image.open(os.path.join(loc,fname))
                    if hasattr( img, '_getexif' ):
                        try:
                            exifinfo = img._getexif()
                        except:
                            exifinfo = None
                        if exifinfo != None:
                            for tag, value in exifinfo.items():
                                decoded = TAGS.get(tag, tag)
                                ret[decoded] = value
                        else:
                            timeArray = time.localtime(os.path.getctime(fname))
                            otherStyleTime = time.strftime("%Y-%m-%d-%H%M%S", timeArray)
                            return str(otherStyleTime).replace(':','-').replace(' ','_')
                except IOError:
                    print('IOERROR/ValueError ' + fname)
    except ValueError:
        print('ValueError ' + fname)

            
    if ret.get('DateTimeOriginal') != None:
        cd = ret.get('DateTimeOriginal')[0:7].replace(':','-').replace(' ','')
        return cd
    else:
        timeArray = time.localtime(os.path.getctime(os.path.join(loc,fname)))
        otherStyleTime = time.strftime("%Y-%m-%d-%H%M%S", timeArray)
        return str(otherStyleTime).replace(':','-').replace(' ','_')
#        print('creation date: '+os.path.getctime(fname).replace(':','-').replace(' ','_') ) 
#        return os.path.getctime(fname).replace(':','-').replace(' ','_')   





def getsize(loc,fname):
    try:
        size1 = os.path.getsize(os.path.join(loc,fname))
    except OSError:
        size1 = -1    
    return size1




def class_files_bytime(folder,desfold,size):
    log = desfold + '\\' +'rename.log'
    if os.path.exists(log):
        os.remove(log)
    for i in os.listdir(folder):
        if os.path.isdir(os.path.join(folder,i)):
            class_files_bytime(os.path.join(folder,i),desfold,size)
        else:
            log = os.path.join(desfold,'rename.log')
            e = os.path.splitext(i)[-1]
            subfld = str(gettime(folder,i))[0:10]
            print('--------------------------')
            print(subfld + '----' + i)

            print('--------------------------')
            if e.lower() not in ('.jpg','.png','jepg','bmp'):
                print(r'1.if e.lower() not in jpg')
                f = open(log,'a')
                f.write(os.path.join(folder,str(i)) +  '| is not renamed')
                f.write('\n')
                f.close()

            
                
                if not os.path.exists(os.path.join(desfold,'others')):
                    print('others is '+'making')
                    os.makedirs(os.path.join(desfold,'others'))
                if os.path.exists(os.path.join(desfold,'others',str(i))):
                    shutil.move(os.path.join(folder,str(i)),os.path.join(desfold,'others',datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+i))
                else:   
                    shutil.move(os.path.join(folder,str(i)),os.path.join(desfold,'others',str(i)))
            elif getsize(folder,i) > size:
                print('2.'+str(getsize(folder,i))+'----------'+str(size))
                t = rename(folder,i) + str(e)
                print(subfld)
                #用 copy2 会保留图片的原始属性
#                print(e)
#                print(folder + '\\'+ str(i))
#                print(desfold+'\\'+ t)
                stringfd = os.path.join(desfold,subfld)
                print(stringfd+'checking')
                if not os.path.exists(stringfd):
                    print(stringfd+'making')
                    os.makedirs(stringfd)
                print(os.path.join(desfold,subfld,t))    
                if os.path.exists(os.path.join(desfold,subfld,t)):
                    if not os.path.exists(os.path.join(desfold,'dup')):
                        print(stringfd+'making')
                        os.makedirs(os.path.join(desfold,'dup'))
                    
                    shutil.move(os.path.join(folder,str(i)),os.path.join(desfold,'dup',datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+t))
                else:    
                    shutil.move(os.path.join(folder,str(i)),os.path.join(desfold,subfld,t))
                f = open(log,'a')
                f.write(os.path.join(folder,i) + '| is renamed')
                f.write('\n')
                f.close()

            else:
                print('xxxxxxxxxxxxxxxxxxx')
                print(i)
                t = rename(folder,i) + str(e)
                print(rename(folder,i))
                #用 copy2 会保留图片的原始属性
#                print(e)
#                print(folder + '\\'+ str(i))
#                print(desfold+'\\'+ t)
                stringfd = os.path.join(desfold,'small')
                print(stringfd+'checking')
                if not os.path.exists(stringfd):
                    print(stringfd+'making')
                    os.makedirs(stringfd)
                if not os.path.exists(os.path.join(desfold,"small",t)):
                    shutil.move(os.path.join(folder,str(i)),os.path.join(desfold,'small',t))
                else:
                    f = open(log,'a')
                    f.write(os.path.join(folder,i) + '| is duplicate and not renamed')
                    f.write('\n')
                    f.close()

def main():
    pass
if __name__ == '__main__':
    main()
