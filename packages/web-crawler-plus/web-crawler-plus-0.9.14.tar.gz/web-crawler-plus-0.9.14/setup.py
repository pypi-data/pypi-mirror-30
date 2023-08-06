#!/usr/bin/env python

from setuptools import setup

setup(name='web-crawler-plus',
      version='0.9.14',
      description='A micro-framework to crawl the web pages with crawlers configs.'
                  ' It can use MongoDB, Elasticsearch and Solr databases to cache and save the extracted data.',
      author='Ravi Raja Merugu',
      author_email='rrmerugu@gmail.com',
      url='https://github.com/invanatech/web-crawler-plus',
      packages=['webcrawler_plus', 'tests',
                'webcrawler_plus.spiders', 'webcrawler_plus.pipelines', 'webcrawler_plus.httpcache',
                'webcrawler_plus.spiders.search_engines', 'webcrawler_plus.utils'],
      install_requires=['Scrapy==1.5.0', 'pysolr==3.7.0', 'pymongo==3.6.1', 'elasticsearch-dsl==6.1.0',
                        "feedparser==5.2.1"]
      )
