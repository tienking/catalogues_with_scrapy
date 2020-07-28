import scrapy
import csv
import json
from os.path import isfile, join, abspath, exists
from os import makedirs, listdir
import urllib.request
import img2pdf
import datetime
#--------------
import requests
import shutil

HISTORY_PATH = "download_history.json"
CATALOGUE_INFO_PATH = abspath("./images_info/")
CATALOGUE_PATH = abspath("./images/")
WEB_PAGES_PATH = "web_pages.csv"

class CatalogueSpider(scrapy.Spider):
    name = 'catalogues'
    
    def __init__(self):
        self.catalogue_pages = self.read_web_data()
        self.cata_history = self.read_history_data()
        self.download_imgs = []
    
    def start_requests(self):
        for catalogue_page in self.catalogue_pages:
            if catalogue_page["download_page"] == "au-catalogues":
                yield scrapy.Request(url=catalogue_page["url"],
                                     callback=self.parse_au_cata,
                                    cb_kwargs=dict(catalogue_page=catalogue_page))
            elif catalogue_page["download_page"] == "winc":
                yield scrapy.Request(url=catalogue_page["url"],
                                     callback=self.parse_winc_cata,
                                    cb_kwargs=dict(catalogue_page=catalogue_page))
            elif catalogue_page["download_page"] == "pnp":
                yield scrapy.Request(url=catalogue_page["url"],
                                     callback=self.parse_pnp_cata,
                                    cb_kwargs=dict(catalogue_page=catalogue_page))

    def parse_winc_cata(self, response, catalogue_page):
        pass
        
    def parse_pnp_cata(self, response, catalogue_page):
        block_all = response.xpath('//div[@class="row favourites-main"]/div/div[@class="content"]')
        for block in block_all:
            block_info = block.xpath('div/b/text()').getall()
            block_name = block_info[0]
            block_date = "No Date"
            if len(block_info) >= 2:
                block_date = block_info[1]
                
            cata_block = block.xpath('div[@class="categoryLandingHeader"]/a')
            for cata in cata_block:
                pdf_link = cata.xpath("@href").get()
                if pdf_link.endswith(".pdf"):
                    location = cata.xpath("text()").get()
                    cata_name = block_name + "_" + block_date + "_" + location.strip()

                    if self.check_catalogue_exists(catalogue_page["name"], pdf_link) == False:
                        self.write_to_file(catalogue_page, cata_name, pdf_link, "pdf")
                        self.write_catalogue_history(catalogue_page["name"], pdf_link)
            
    def parse_au_cata(self, response, catalogue_page):
        cata_all = response.xpath('//div[@class="leaflet-detail"]/a[@class="leaflet-img-mobile-detail-flex"]/@href').getall()
        for cata in cata_all:
            img_urls = []
            cata_page = response.urljoin(cata)
            yield scrapy.Request(url=cata_page,
                                 callback=self.parse_au_detail,
                                cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls))

    def parse_au_detail(self, response, catalogue_page, img_urls):
        page = response.url.split("/")[-1]
        root_url = response.css('a.ga-classic-leaflet::attr(href)').get()
        img_url = response.css('img#leaflet::attr(src)').get()
        img_path = response.urljoin(img_url)
        
        img_urls.append(img_path)
        
        next_page = response.xpath('//div[@class="numbers"]/a[@rel="next"]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_au_detail,
                                 cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls))
        else:
            last_page_url = response.request.url
            cata_name = response.xpath("//h1[@class='leaflet-title']/text()").get().split("\n")[1]
            if self.check_catalogue_exists(catalogue_page["name"], last_page_url) == False:
                self.write_to_file(catalogue_page, cata_name, img_urls, "jpg")
                self.write_catalogue_history(catalogue_page["name"], last_page_url)

    def write_to_file(self, catalogue_page, cata_name, img_urls, download_ext):
        if not exists(CATALOGUE_INFO_PATH):
            makedirs(CATALOGUE_INFO_PATH)
        with open(join(CATALOGUE_INFO_PATH, catalogue_page["name"] + ".csv"), "a", encoding='utf-8', newline="") as im_f:
            out_reader = csv.writer(im_f)
            
            if type(img_urls) == list:
                for img in img_urls:
                    out_reader.writerow([str(datetime.datetime.now().date()),catalogue_page["name"],catalogue_page["url"],catalogue_page["download_page"],cata_name,img])
            else:
                out_reader.writerow([str(datetime.datetime.now().date()),catalogue_page["name"],catalogue_page["url"],catalogue_page["download_page"],cata_name,img_urls])
            self.download_imgs.append([catalogue_page["name"],str(datetime.datetime.now().date()),cata_name,img_urls,download_ext])

    def check_catalogue_exists(self, cata_name, last_page_url):
        if cata_name not in self.cata_history.keys():
            return False
        elif last_page_url not in self.cata_history[cata_name]:
            return False
        else:
            return True
            
    def write_catalogue_history(self, cata_name, last_page_url):
        if cata_name not in self.cata_history.keys():
            self.cata_history[cata_name] = [last_page_url]
        else:
            self.cata_history[cata_name].append(last_page_url)

    def closed(self, reason):
        if len(self.download_imgs) > 0:
            with open(HISTORY_PATH, "w") as dh_file:
                json.dump(self.cata_history, dh_file)
            print("---DOWNLOADING CATALOGUES---")
            self.download_catalogues()
            print("---DONE---")
            
    def read_history_data(self):
        his_data = None

        if isfile(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as dh_file:
                his_data = json.load(dh_file)
        else:
            his_data = {}
        return his_data

    def read_web_data(self):
        cata_pages = []
        with open(WEB_PAGES_PATH, "r") as web_file:
            file_reader = csv.reader(web_file)
            
            for row in file_reader:
                cata_dict = {}
                cata_dict["name"] = row[0]
                cata_dict["url"] = row[1]
                cata_dict["download_page"] = row[2]
                cata_pages.append(cata_dict)
                
        return cata_pages
        
    def download_catalogues(self):
        if not exists(CATALOGUE_PATH):
            makedirs(CATALOGUE_PATH)
        for download_img in self.download_imgs:
            cata_uni_name = download_img[1] + "_" + download_img[2]
            output_path = join(CATALOGUE_PATH,download_img[0],cata_uni_name)
            if not exists(output_path):
                makedirs(output_path)
            if download_img[-1] == "jpg":
                self.download_jpg_to_pdf(download_img, download_img[2], output_path)
            elif download_img[-1] == "pdf":
                self.download_pdf(download_img, download_img[2], output_path)
    
    def download_pdf(self, download_img, cata_name, output_path):
        r = requests.get(download_img[3], stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            with open(join(output_path, cata_name + ".pdf"), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    
    def download_jpg_to_pdf(self, download_img, cata_name, output_path):
        index = 1
        for img_url in download_img[3]:
            img_path = join(output_path,"page_" + str(index).rjust(3, '0') + ".jpg")
            #--------------
            r = requests.get(img_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(img_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            #--------------
            #urllib.request.urlretrieve(img_url, img_path)
            index += 1
        self.images_to_pdf(output_path, cata_name)
    
    def images_to_pdf(self, output_path, cata_name):
        with open(join(output_path, cata_name + ".pdf"), "wb") as pdf_file:
            pdf_file.write(img2pdf.convert([join(output_path, img) for img in listdir(output_path) if img.endswith(".jpg")]))