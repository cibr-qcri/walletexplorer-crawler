from datetime import datetime
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from w3lib.html import remove_tags

from ..items import WalletexplorerItem


class WalletExplorerCrawler(scrapy.Spider):
    name = "walletexplorer"
    base_url = "https://www.walletexplorer.com"
    allowed_domains = ["walletexplorer.com"]
    start_urls = ["https://www.walletexplorer.com/"]

    def parse(self, response):
        table_data = response.xpath('/html//table[@class = "serviceslist"]//td')
        service_map = {0: "exchange", 1: "pool", 2: "service/other", 3: "gambling", 4: "old/historic"}
        for key, value in service_map.items():
            services = table_data[key].xpath("//td//li")
            for service in services:
                exchange_urls = service.xpath(".//a/@href").extract()
                service_name = self.process_token(service).strip().split(" ")[0]
                for uri in exchange_urls:
                    addresses_url = self.base_url + uri + "/addresses"
                    yield scrapy.Request(addresses_url, meta={"type": value, "name": service_name},
                                         dont_filter=False, callback=self.parse_service, errback=self.handle_error)

    def parse_service(self, response):
        item = WalletexplorerItem()
        table_data = response.xpath('/html//table//td')
        address_list = list()
        for i in range(0, len(table_data), 4):
            address = self.process_token(table_data[i])
            address_list.append(address)
        name = response.meta["name"]
        item["addresses"] = address_list
        item["type"] = response.meta["type"]
        item["name"] = response.meta["name"]
        item["response"] = response
        item["timestamp"] = int(datetime.now().timestamp() * 1000)

        if 'page' not in response.url:
            service_url = response.xpath('/html//span[@class = "showother"]//a[1]/@href')[0].extract() \
                if "." in name else ""
            page_count = int(response.xpath('/html//div[@class = "paging"]').re('[\\d]+')[1])
            page_url = 'https://www.walletexplorer.com/wallet/' + name + '/addresses?page='
            for page in range(page_count):
                yield scrapy.Request(page_url + str(page), meta={"type": response.meta["type"], "name": name,
                                                                 "service_url": service_url}, dont_filter=False,
                                     callback=self.parse_service, errback=self.handle_error)
        else:
            service_url = response.meta["service_url"]
        item["service_url"] = service_url

        yield item

    def handle_error(self, failure):
        self.logger.debug(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    @staticmethod
    def process_token(value):
        return remove_tags(value.extract()).strip('\r\t\n')

