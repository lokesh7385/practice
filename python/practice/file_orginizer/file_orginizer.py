import os
import shutil

os.chdir(r'E:\python\python\practice\file_orginizer')

option = input("Enter your option (r for rename, d for delete, c for copy and m for move)")

folder_name = "demo"

if option == "r":
    for file in os.listdir():
        if file in("file_orginizer.py",folder_name):
            continue
        name,ext = os.path.splitext(file)
        splitted = name.split("_")
        new_name = f"{splitted[0].zfill(2)}_{splitted[1]}{ext}"
        os.rename(file,new_name)
elif option == "m":
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    for file in os.listdir():
        if file in ("file_orginizer.py",folder_name):
            continue
        shutil.move(file,folder_name)
elif option == "c":
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
#.copy is for copy data .copy2 to copy with metadata
    for file in os.listdir():
        if file in ("file_orginizer.py",folder_name):
            continue
        shutil.copy(file,folder_name)
        # shutil.copy2(file,"demo")
elif option == "d":
# to delete non empty directory 
    shutil.rmtree(folder_name)
# to delete empty directory
    # os.rmdir("demo")
else:
    print("Invalid option")