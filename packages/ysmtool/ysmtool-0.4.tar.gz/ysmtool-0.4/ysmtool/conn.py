#!/usr/bin/python
# -*- coding: utf-8 -*-
import time,re,thread,os
import pymongo
import datetime
import random


connection_sms= pymongo.MongoClient('47.91.252.126:1111')
db_sms= connection_sms.sms
db_sms.authenticate('sms','140520')

connection_sites= pymongo.MongoClient('47.91.252.126:1111')
db_sites= connection_sites.xkw
db_sites.authenticate('xkw','140520')
