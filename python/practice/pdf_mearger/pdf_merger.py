from PyPDF2 import PdfMerger

import glob

#*.pdf means all pdf files in the directory 

files = glob.glob("E:\python\python\practice\pdf_mearger\*.pdf")

merger = PdfMerger()

for file in files :
    merger.append(file)

merger.write("merged.pdf")

merger.close()