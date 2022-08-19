import img2pdf
import requests
from shutil import copyfileobj
from os.path import join
from os.path import exists
import os

def download_jpg_to_pdf(img_urls, cata_name, jpg_path, output_path):
    index = 1
    for img_url in img_urls:
        if ".webp" in img_url or ".jpg" in img_url:
            img_path = join(jpg_path,"page_" + str(index).rjust(3, '0') + ".jpg")
            #--------------
            r = requests.get(img_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(img_path, 'wb') as f:
                    r.raw.decode_content = True
                    copyfileobj(r.raw, f)
            #--------------
            index += 1
    output_filename =  merge_jpg_to_pdf(cata_name, jpg_path, output_path)
    return output_filename

def merge_jpg_to_pdf(cata_name, jpg_path, output_path):
    output_filename = join(output_path, cata_name + ".pdf")
    
    index = 1
    while exists(output_filename):
        output_filename = join(output_path, cata_name + " ({0})".format(index) + ".pdf")
        index += 1
        
    jpg_files = [join(jpg_path, img) for img in os.listdir(jpg_path) if img.endswith(".jpg")]
    with open(output_filename, "wb") as pdf_file:
        pdf_file.write(img2pdf.convert(jpg_files))

    for jpg_file in jpg_files:
        os.remove(jpg_file)
        
    return output_filename
        
    