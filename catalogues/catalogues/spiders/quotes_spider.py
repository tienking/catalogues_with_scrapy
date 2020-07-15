import scrapy

class CatalogueSpider(scrapy.Spider):
    name = 'catalogues'
    
    def __init__(self):
        self.img_urls = []
    
    def start_requests(self):
        urls = [
            'https://au-catalogues.com/david-jones-ads/catalogue-23506-0',
            'https://au-catalogues.com/david-jones-ads/catalogue-26587-0',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-1]
        root_url = response.css('a.ga-classic-leaflet::attr(href)').get()
        img_url = response.css('img#leaflet::attr(src)').get()
        img_path = response.urljoin(img_url)
        self.img_urls.append(img_path)
        
        next_page = response.xpath('//div[@class="numbers"]/a[@rel="next"]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        
        self.to_file("all_images.txt")

            
    def to_file(self, output_path):
        with open(output_path, "a") as im_f:
            for im in self.img_urls:
                im_f.write(im)
                im_f.write("\n")