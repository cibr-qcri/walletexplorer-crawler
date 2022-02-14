import os
from hashlib import sha256

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from scrapy.utils.project import get_project_settings


class WalletexplorerPipeline(object):

    def __init__(self):
        self.dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings = get_project_settings()
        self.server = self.settings['ELASTICSEARCH_CLIENT_SERVICE_HOST']
        self.port = self.settings['ELASTICSEARCH_CLIENT_SERVICE_PORT']
        self.port = int(self.port)
        self.username = self.settings['ELASTICSEARCH_USERNAME']
        self.password = self.settings['ELASTICSEARCH_PASSWORD']
        self.index = self.settings['ELASTICSEARCH_INDEX']
        self.type = self.settings['ELASTICSEARCH_TYPE_PROFILE']

        if self.port:
            uri = "http://%s:%s@%s:%d" % (self.username, self.password, self.server, self.port)
        else:
            uri = "http://%s:%s@%s" % (self.username, self.password, self.server)

        self.es = Elasticsearch([uri])

    def process_item(self, item, spider):
        timestamp = item["timestamp"]
        response = item["response"]
        service_name = response.meta["name"]
        address_list = item["addresses"]
        service_url = item["service_url"]
        url = 'https://www.walletexplorer.com/wallet/' + response.url.split('/')[4]

        document_hash = sha256(service_name.encode("utf-8")).hexdigest()

        soup = BeautifulSoup(response.text, "lxml")
        title = soup.title.string.strip() if soup.title else ""

        tag = {
            'timestamp': timestamp,
            'type': 'service',
            'source': 'walletexplorer',
            "info": {
                "domain": 'www.walletexplorer.com',
                "url": service_url,
                "title": title,
                "tags": {
                    "cryptocurrency": {
                        "address": {
                            "btc": address_list
                        }
                    },
                    "wallet": {
                        "service_type": response.meta["type"],
                        "name": service_name,
                        "url": url
                    },
                },
                "raw_data": response.text
            }
        }

        update_tag = {
            "script": {
                "source": "ctx._source.info.tags.cryptocurrency.address.btc.add(params.addresses)",
                "lang": "painless",
                "params": {
                    "addresses": address_list
                }
            }
        }

        if 'page' in response.url:
            self.es.update(index=self.index, id=document_hash, body=update_tag)
        else:
            self.es.index(index=self.index, id=document_hash, body=tag)

        spider.logger.info("Page exported to ElasticSearch index %s at %s:%s" % (self.index, self.server, self.port))

        return item




