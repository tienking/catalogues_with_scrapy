#---Scrapy---
import scrapy
#---Files---
import csv
import json
#---Operation---
from os.path import isfile, join, abspath, exists
from os import makedirs, listdir
#---Ad-hoc Library---
import requests
import img2pdf
import shutil
from datetime import datetime, timedelta

# Get PATH conf
from conf import PATH

def get_next_monday():
    # Get next Monday from current date
    cur_time = datetime.now()
    last_monday = cur_time - timedelta(days=cur_time.weekday())
    last_monday = last_monday.replace(hour=9, minute=0)
    date_range = cur_time - last_monday
    # Check today is Monday (time before 8h00 AM)
    if date_range.days == -1:
        next_monday_folder = last_monday.strftime("%Y%m%d")
    else:
        next_monday = cur_time - timedelta(days=cur_time.weekday()-7)
        next_monday_folder = next_monday.strftime("%Y%m%d")
    
    return next_monday_folder

HISTORY_PATH = join(PATH["download_history_path"],"test_download_history.json")
CATALOGUE_INFO_PATH = abspath(join(PATH["download_detail_path"],"test_images_info"))
CATALOGUE_PATH = abspath(join(PATH["download_path"],"test_images","{0}".format(get_next_monday())))
WEB_PAGES_PATH = join(PATH["download_input_path"],"test_web_pages.csv")
DOWNLOAD_ERROR_PATH = join(PATH["download_error_path"],"test_download_error.csv")

class CatalogueSpider(scrapy.Spider):
    name = 'test-catalogue'
    
    def __init__(self):
        #---Catalogues---
        self.catalogue_pages = self.read_web_data()
        self.cata_history = self.read_history_data()
        self.download_imgs = {}
        self.error_cata = 0
    
    def start_requests(self):
        for catalogue_page in self.catalogue_pages:
            if catalogue_page["download_page"] == "au-catalogues":
                yield scrapy.Request(url=catalogue_page["url"],
                                     callback=self.parse_au_cata,
                                    cb_kwargs=dict(catalogue_page=catalogue_page))

    def parse_au_cata(self, response, catalogue_page):
        cata_all = response.xpath('//div[@class="leaflet-detail"]/a[@class="leaflet-img-mobile-detail-flex"]/@href').extract()
        print(cata_all)
        for cata in cata_all:
            cata_page = response.urljoin(cata)
            yield scrapy.Request(url=cata_page,
                                 callback=self.check_last_page_exists,
                                cb_kwargs=dict(catalogue_page=catalogue_page, first_page=cata_page))

    def check_last_page_exists(self, response, catalogue_page, first_page):
        page_count = int(response.xpath('//div[@class="numbers"]/a/text()').extract()[-1]) - 1
        last_page_url = "-".join(first_page.split("-")[:-1]) + "-" + str(page_count)
        
        if self.check_catalogue_exists(catalogue_page["name"], last_page_url) == False:
            img_urls = []
            
            next_page = response.xpath('//div[@class="numbers"]/a[@rel="next"]/@href').extract_first()
            if next_page is not None:
                root_element = response.xpath('//tr/td[@class="leaflet-detail-big monitoring-leaflet"]')
                img_url = root_element.css("picture img::attr(src)").extract_first()
                if img_url is None:
                    img_url = root_element.css("a amp-img::attr(src)").extract_first()
                if img_url is None:
                    img_url = root_element.css("a img::attr(src)").extract_first()
                if img_url is None:
                    img_url = root_element.css("img::attr(src)").extract_first()
                if img_url is None:
                    img_url = root_element.css("amp-img::attr(src)").extract_first()
                
                img_path = response.urljoin(img_url)
                img_urls.append(img_path)

                last_page_response = response
                last_page_url = response.request.url

                next_page = response.urljoin(next_page)
            
                yield scrapy.Request(url=next_page,
                                     callback=self.parse_au_detail,
                                     cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls, last_page_response=last_page_response))

    def parse_au_detail(self, response, catalogue_page, img_urls, last_page_response):
        next_page = response.xpath('//div[@class="numbers"]/a[@rel="next"]/@href').get()
        if next_page is not None:
            root_element = response.xpath('//tr/td[@class="leaflet-detail-big monitoring-leaflet"]')
            img_url = root_element.css("picture img::attr(src)").extract_first()
            if img_url is None:
                img_url = root_element.css("a amp-img::attr(src)").extract_first()
            if img_url is None:
                img_url = root_element.css("a img::attr(src)").extract_first()
            if img_url is None:
                img_url = root_element.css("img::attr(src)").extract_first()
            if img_url is None:
                img_url = root_element.css("amp-img::attr(src)").extract_first()
               
            img_path = response.urljoin(img_url)
            img_urls.append(img_path)
            
            last_page_response = response
            last_page_url = response.request.url

            next_page = response.urljoin(next_page)

            yield scrapy.Request(url=next_page,
                                 callback=self.parse_au_detail,
                                 cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls, last_page_response=last_page_response))
        else:
            last_page_url = last_page_response.request.url
            if self.check_catalogue_exists(catalogue_page["name"], last_page_url) == False:
                last_page_name = "-".join(last_page_response.xpath("//div[@class='header']/h1/text()").get().strip().replace("\n","").replace("/","").split(" - ")[:-1])
                self.write_to_file(catalogue_page, last_page_name, img_urls, last_page_url)
                #self.write_catalogue_history(catalogue_page["name"], last_page_url)

    def write_to_file(self, catalogue_page, last_page_name, img_urls, last_page_url):
        if not exists(CATALOGUE_INFO_PATH):
            makedirs(CATALOGUE_INFO_PATH)
        with open(join(CATALOGUE_INFO_PATH, catalogue_page["name"] + ".csv"), "a", encoding='utf-8', newline="") as im_file:
            out_writer = csv.writer(im_file)
            
            if type(img_urls) == list:
                for img in img_urls:
                    out_writer.writerow([str(datetime.now().date()),catalogue_page["name"],catalogue_page["url"],catalogue_page["download_page"],last_page_name,img])
            else:
                out_writer.writerow([str(datetime.now().date()),catalogue_page["name"],catalogue_page["url"],catalogue_page["download_page"],last_page_name,img_urls])
            self.download_imgs[last_page_url] = ([catalogue_page["name"],str(datetime.now().date()),last_page_name,img_urls])

    def check_catalogue_exists(self, cata_name, last_page_url):
        if cata_name not in self.cata_history.keys():
            return False
        elif last_page_url not in self.cata_history[cata_name]:
            return False
        else:
            return True

    def closed(self, reason):
        
        if len(self.download_imgs) > 0:
            print("\t>> DOWNLOADING CATALOGUES...\n")
            self.download_catalogues()
            print("\t[DONE]\n")

            with open(HISTORY_PATH, "w") as dh_file:
                dh_file.write(json.dumps(self.cata_history, indent = 6))
                
        if self.error_cata == 0:
            print("\n")
            print("\t----------------------------------------------------")
            print("\t--------- DOWNLOAD COMPLETED WITH NO ERROR ---------")
            print("\t----------------------------------------------------")
            print("\n")
        else:
            print("\n")
            print("\t----------------------------------------------------")
            print("\t--- DOWNLOAD COMPLETED WITH {0} ERROR CATALOGUE(S) ---".format(self.error_cata))
            print("\t------ Please check download_error folder !!!! -----")
            print("\t----------------------------------------------------")
            print("\n")
            
    def read_history_data(self):
        his_data = None

        if isfile(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as dh_file:
                his_data = json.loads(dh_file.read())
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
        for last_page_url, download_img in self.download_imgs.items():
            try:
                cata_uni_name = download_img[2]
                output_path = join(CATALOGUE_PATH,download_img[0],cata_uni_name)

                if exists(output_path):
                    cata_index = 1
                    temp_path = output_path
                    while exists(temp_path):
                        temp_path = output_path + "_" + str(cata_index)
                        cata_index += 1
                    
                    output_path = temp_path
                makedirs(output_path)
                        
                self.download_jpg_to_pdf(download_img, download_img[2], output_path)
                print("\t[SUCCESS]: {0}".format(cata_uni_name))
                print("\t---------------\n")
                self.write_catalogue_history(download_img[0], last_page_url)
            except Exception as e:
                shutil.rmtree(output_path, ignore_errors=True)
                print("\t[ERROR]: {0}".format(cata_uni_name))
                print("\t---------------\n")
                self.write_error_history(download_img[0], last_page_url, str(e).replace("\n", " "))
                self.error_cata += 1

    def write_catalogue_history(self, cata_name, last_page_url):
        if cata_name not in self.cata_history.keys():
            self.cata_history[cata_name] = [last_page_url]
        else:
            self.cata_history[cata_name].append(last_page_url)

    def write_error_history(self, cata_name, last_page_url, exception_detail):
        with open(DOWNLOAD_ERROR_PATH, "a", encoding='utf-8', newline="") as err_file:
            err_writer = csv.writer(err_file)
            err_writer.writerow([str(datetime.now().date()),cata_name,last_page_url,exception_detail])

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
            index += 1
        self.images_to_pdf(output_path, cata_name)
    
    def images_to_pdf(self, output_path, cata_name):
        with open(join(output_path, cata_name + ".pdf"), "wb") as pdf_file:
            pdf_file.write(img2pdf.convert([join(output_path, img) for img in listdir(output_path) if img.endswith(".jpg")]))