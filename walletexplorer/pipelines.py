import os
from hashlib import sha256

from .es7 import ES7

from bs4 import BeautifulSoup
from scrapy.utils.project import get_project_settings


class WalletexplorerPipeline(object):

    def __init__(self):
        self.dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings = get_project_settings()
        self.es = ES7()

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
            self.es.update_report(update_tag, document_hash)
        else:
            self.es.persist_report(tag, document_hash)

        return item




