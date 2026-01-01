import os
import shutil

path = input("Enter path of directory to sort:")
file = os.listdir(path)

for file in file:

    filename,extension = os.path.splitext(file)
    extension =extension[1:]

#this is for sorting files if the folder alerady exists

    if os.path.exists(path+'/'+extension):
        shutil.move(path+'/'+file,path+'/'+extension+'/'+file)

#this is for sorting files if the folder does not exist
    else:
        os.makedirs(path+'/'+extension)
        shutil.move(path+'/'+file,path+'/'+extension+'/'+file)
