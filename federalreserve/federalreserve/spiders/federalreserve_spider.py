import scrapy

from scrapy.selector import Selector
from scrapy.http import Request
from urlparse import urljoin
from federalreserve.items import FederalreserveItem
import time

class VitailsSpider(scrapy.Spider):
	name = "federal"
	allowed_domains =["federalreserve.gov"]
	start_urls = ["https://www.federalreserve.gov/releases/h10/hist/" ]

	def parse(self, response):
		#time.sleep(10)
		#print "++++++response.url:", response.url
		# for i in response.xpath(".//*[@class='statistics']//tr/th/a"):
		# 	print ">>>",i.xpath("text()").extract()
		# country names
		country_s = response.xpath(".//*[@class='statistics']//tr/th/a[@href]  | .//*[@class='statistics']//tr/th[.//sup]/a[@href]")
		# country hrefs
		#monetary_units
		monetary_unit_s = response.xpath(".//*[@class='statistics']//tr/td")
		#//*[@id="printThis"]/table/tbody/tr/td/text()
		for country, monetary_unit  in zip(country_s, monetary_unit_s ):
			item = FederalreserveItem()
			item["country"] = country.xpath('text()').extract()[0]
			item["monetary_unit"] = monetary_unit.xpath('text()').extract()[0]
			href = country.xpath('@href').extract()[0]

			if href:
				if 'http://' not in href:
					href = urljoin(response.url, href)
					#yield scrapy.Request(href, callback=self.prepare_to_crawl)
					yield scrapy.Request(href,
											meta={'part_items': FederalreserveItem(country=item["country"], monetary_unit=item["monetary_unit"])},
											callback=self.parse_productdetail)
	def parse_productdetail(self, response):
		print "++++++response.url:", response.url
		FederalreserveItem = response.meta['part_items']
		
		#FederalreserveItem['date_prices']={}


		date_s = response.xpath(".//*[@class='statistics']//tr/th[@id='r1']")

		FederalreserveItem['date_prices']=[]
		price_s = response.xpath(".//*[@class='statistics']//tr/td[@headers]")
		# for i in price_s:
		# 	print i.xpath('text()').extract()[0]
		for date , price in zip(date_s, price_s ):
			item={}
			date = date.xpath('text()').extract()[0]
			item['date'] = date.split()[0]
			price = price.xpath('text()').extract()[0]
			item['price'] = price.split()[0]
			#print item
			FederalreserveItem['date_prices'].append(item)
			
			#FederalreserveItem['date_prices']['date']= date.xpath('text()').extract()[0]
			#FederalreserveItem['date_prices']['price']= price.xpath('text()').extract()[0]

		yield FederalreserveItem

