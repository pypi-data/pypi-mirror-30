#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient

class Xxxx:
    def __init__(self):
        # Conecta ao banco de dados
        self.mongo_server = MongoClient("localhost", 27017)


Xxxx()