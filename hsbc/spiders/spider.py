import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import HhsbcItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class HhsbcSpider(scrapy.Spider):
	name = 'hsbc'
	start_urls = ['https://www.business.hsbc.com.br/en-gb/insights?contentType=AaO_YOh5iUOb0Q4Xquv1ew&topics=YWxs&sectors=YWxs&regions=YWxs']

	def parse(self, response):
		post_links = response.xpath('//h2[@class="article-promo__heading"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="pagination__next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="page-description__meta"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="page-description__summary"]//text()').getall() + response.xpath('//div[@class="text text--editorial  "]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=HhsbcItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
