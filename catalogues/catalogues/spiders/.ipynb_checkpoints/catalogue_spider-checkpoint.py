import scrapy
import csv
import json
from os.path import isfile

class CatalogueSpider(scrapy.Spider):
    name = 'catalogues'
    
    def __init__(self):
        self.catalogue_pages = self.read_web_data()
        self.cata_history = self.read_history_data()
    
    def start_requests(self):
        for catalogue_page in self.catalogue_pages:
            yield scrapy.Request(url=catalogue_page["url"],
                                 callback=self.parse_cata,
                                cb_kwargs=dict(catalogue_page=catalogue_page))
            
    def parse_cata(self, response, catalogue_page):
        cata_all = response.xpath('//div[@class="leaflet-detail"]/a[@class="leaflet-img-mobile-detail-flex"]/@href').getall()
        for cata in cata_all:
            img_urls = []
            cata_page = response.urljoin(cata)
            yield scrapy.Request(url=cata_page,
                                 callback=self.parse_detail,
                                cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls))

    def parse_detail(self, response, catalogue_page, img_urls):
        page = response.url.split("/")[-1]
        root_url = response.css('a.ga-classic-leaflet::attr(href)').get()
        img_url = response.css('img#leaflet::attr(src)').get()
        img_path = response.urljoin(img_url)
        
        img_urls.append(img_path)
        
        next_page = response.xpath('//div[@class="numbers"]/a[@rel="next"]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_detail,
                                 cb_kwargs=dict(catalogue_page=catalogue_page, img_urls=img_urls))
        else:
            last_page_url = response.request.url
            cata_name = response.xpath("//h1[@class='leaflet-title']/text()").get().split("\n")[1]
            if self.check_catalogue_exists(catalogue_page["name"], last_page_url) == False:
                self.write_to_file(catalogue_page, cata_name, img_urls, last_page_url)
                self.write_catalogue_history(catalogue_page["name"], last_page_url)

    def write_to_file(self, catalogue_page, cata_name, img_urls, last_page_url):
        with open(catalogue_page["name"] + ".csv", "a", encoding='utf-8', newline="") as im_f:
            out_reader = csv.writer(im_f)
            for img in img_urls:
                out_reader.writerow([catalogue_page["name"],catalogue_page["url"],catalogue_page["download_page"],cata_name,img])

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
        with open("download_history.json", "w") as dh_file:
            json.dump(self.cata_history, dh_file)
            
    def read_history_data(self):
        his_data = None
        history_file_path = "download_history.json"
        if isfile(history_file_path):
            with open(history_file_path, "r") as dh_file:
                his_data = json.load(dh_file)
        else:
            his_data = {}
        return his_data

    def read_web_data(self):
        cata_pages = []
        with open("test.csv", "r") as web_file:
            file_reader = csv.reader(web_file)
            
            for row in file_reader:
                cata_dict = {}
                cata_dict["name"] = row[0]
                cata_dict["url"] = row[1]
                cata_dict["download_page"] = row[2]
                cata_pages.append(cata_dict)
                
        return cata_pages