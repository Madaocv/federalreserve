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
		country_s = response.xpath(".//*[@class='statistics']//tr/th/a[@href]  | .//*[@class='statistics']//tr/th[.//sup]/a[@href]")
		monetary_unit_s = response.xpath(".//*[@class='statistics']//tr/td")
		for country, monetary_unit  in zip(country_s, monetary_unit_s ):
			item = FederalreserveItem()
			item["country"] = country.xpath('text()').extract()[0]
			item["monetary_unit"] = monetary_unit.xpath('text()').extract()[0]
			href = country.xpath('@href').extract()[0]
			if href:
				if 'http://' not in href:
					href = urljoin(response.url, href)
					yield scrapy.Request(href,
											meta={'part_items': FederalreserveItem(country=item["country"], monetary_unit=item["monetary_unit"])},
											callback=self.parse_productdetail)
	def parse_productdetail(self, response):
		print "++++++response.url:", response.url
		FederalreserveItem = response.meta['part_items']
		date_s = response.xpath(".//*[@class='statistics']//tr/th[@id='r1']")
		FederalreserveItem['date_prices']=[]
		price_s = response.xpath(".//*[@class='statistics']//tr/td[@headers]")
		for date , price in zip(date_s, price_s ):
			item={}
			date = date.xpath('text()').extract()[0]
			item['date'] = date.split()[0]
			price = price.xpath('text()').extract()[0]
			item['price'] = price.split()[0]
			FederalreserveItem['date_prices'].append(item)
		yield FederalreserveItem

