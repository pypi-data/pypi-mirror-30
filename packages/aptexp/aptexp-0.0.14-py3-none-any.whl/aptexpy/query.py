# -*- coding: utf-8 -*-
import pymongo

class MongoQuery:

    __client = None
    __db = None
    __fields = None

    head = []

    def __init__(self, fields={'stix_report':{"Title" : 1, "_id" : 1, "Date" : 1, "Tag" : 1,"vendors" : 1, "URL": 1}},
                                params={'host':'127.0.0.1:27017','db':'mongo_engine_db'}):
        
        self.__client = pymongo.MongoClient(params['host'])
        self.__db = self.__client[params['db']]
        self.__fields = fields

    def test(self):
        print(self.parse_collection())


    def parse_collection(self):

        result = []
        for k, v in self.__fields.items():
            db_coll = self.__db[k]
            self.__parse_field_txt(db_coll, v, result)

        # reverse result
        # result = list(zip(*result))

        return result

    def __parse_field_txt(self, db_coll, text, res):
        isempty = True if(res == []) else False
        cursor = db_coll.find({},text)

        n = 0
        keys = []

        for x in cursor:
            record = []
            for k,v in x.items():
                record.append(v)
            if(isempty):
                res.append(record)
            else:
                res[n].extend(record)
                n = n+1

            if(keys==[]):
                keys = list(x.keys())
                print(keys) 
        self.head.extend(keys)

if __name__ == '__main__':

    query = MongoQuery(fields={'stix_report':{"_id" : 0, "Title" : 1, "vendors" : 1, "URL": 1}})

    query.test()


