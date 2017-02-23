# ds153719.mlab.com:53719/hs_deck Home : { db : "hs_deck" }
# http://dev.youngkyu.kr/23

import pymongo
import datetime


client = pymongo.MongoClient('mongodb://hs_deck:12345678@ds153719.mlab.com:53719/hs_deck')
db = client.hs_deck
collection = db.hs_deck

#post = {
#    "author": "Mike",
#    "text": "My first blog post!",
#    "tags": ["mongodb", "python", "pymongo"],
#    "date": datetime.datetime.today().month
#}


#post_id = collection.insert(post)

#post1 = {
#    "author": "Mike",
#    "text": "My first blog post!",
#    "tags": ["mongodb", "python", "pymongo"],
#    "date": datetime.datetime.today().month
#}

#post_id1 = collection.insert(post1)

print(db.collection_names())

for data in collection.find({"date": 2}):
    print(data)
