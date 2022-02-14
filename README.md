# WalletExplorerCrawler

A basic scrapper made in python with [scrapy framework](https://scrapy.org/) supports to -
* Scrape services & associated BTC addresses from [walletexplorer](https://www.walletexplorer.com/).
* Push the output to ElasticSearch.

At the moment crawler only outputs to the ElasticSearch.
### Kubernetese Deployment
***Prerequisites***
1. Kubernetese cluster
2. ElasticSearch cluster

***Clone BlockStack repository***
```sh
git clone https://github.com/qcri/BlockStack.git
cd BlockStack
```
***Install WalletExplorer Crawler***
Install walletexplorer crawler with the release name ```crawler-walletexplorer```
```sh
helm install crawler-walletexplorer -f k8s/config/walletexplorer-crawler
```
### Output Format
WalletExplorer crawler output crawled services to the elasticsearch in following format
```
{
"timestamp": timestamp,
"type": "service",
"source": "walletexplorer",
"info": {
  "domain": domain,
  "url": crawled_url,
  "title": title,
  "external_links: {
    "href_urls": {
        "web": [www_urls],
        "onion": [onion_urls]
    }
  },
  "tags": {
    "cryptocurrency": {
      "address": {
        "btc": [btc_addrs]
      }
    },
    "wallet": {
        "name": name,
        "service": {
            "url": service_url,
            "type": "exchange"|"pool"|"gambling"|"others"|"old"
        },
        "size": num_addr,
        "volume" num_txes
    }
  },
  "raw_data": raw_data
}
```


---

This project is part of [CIBR](https://github.com/qcri/cibr).
