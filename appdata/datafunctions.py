import os
import sys
import time
import pymongo
from scrapingfunctions import *
from pymongo.errors import ConnectionFailure

MONGO_URI = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
GLOBAL_COUNT = 0

def connect_to_db(some_address):
    try:
        client = pymongo.MongoClient(some_address)
        db = client.flaskdb
    except Exception as e:
        print("Could not establish connection to db. Got error:", file=sys.stderr)
        print(str(e))
        return
    return db, client

def add_item_to_database(item, db):
    try:
        db.blocket.insert_one(item)
        print("Added " + item['title'] + " to database.", file=sys.stderr)
    except Exception as e:
        print("Could not add item. Trying next.", file=sys.stderr)
        print(e)
    return True

def add_page_to_db(index, db, old_links):
    print("On page number: " + str(index), file=sys.stderr)
    #get all items on page
    links = get_adds_on_page_no(index)
    for link in links:
        #stopping condition
        if link in old_links:
            print("All links added", file=sys.stderr)
            return
        #scrape item by link
        blocket_item = get_item_info(link)
        item_added = add_item_to_database(blocket_item, db)
    return add_page_to_db(index+1, db, old_links)

def get_old_links(db):
    links_from_db = db.blocket.find({}).sort("$natural", -1).limit(500)
    old_links = []
    for link in links_from_db:
        old_links.append(link['link'])
    return old_links

def get_old_adds(days_old, db):
    date = datetime.today() - timedelta(days=days_old)
    date = date.strftime('%Y-%m-%d')
    cur = db.blocket.find({
        "time": {"$regex": date}
        })
    links = []
    for item in cur:
        links.append(item["link"])
    return links

def check_sold_job():
    #wierd way of checking if conection is up
    db, client = connect_to_db(MONGO_URI)
    try:
        client.admin.command("ismaster")
        #get all adds from the day 20 days ago
        links = get_old_adds(0, db)
        print(links, file=sys.stderr)
        for link in links:
            print(link, file=sys.stderr)
            sold = check_if_removed(link)
            db.blocket.update_one(
                {"link":link},
                {"$set" : {"sold":str(sold)}})
            log = str("is sold? " + link + " : " + str(sold))
            print(log, file=sys.stderr)
    except ConnectionFailure as e:
        print(str(e), file=sys.stderr)
    client.close()
    return

def start_scrape_job():
    print("Running job", file=sys.stderr)
    global GLOBAL_COUNT
    GLOBAL_COUNT = GLOBAL_COUNT + 1
    db, client = connect_to_db(MONGO_URI)
    try:
        #wierd way of checking if conection is up
        client.admin.command("ismaster")
        old_links = get_old_links(db)
        add_page_to_db(1, db, old_links)
    except ConnectionFailure as e:
        print(str(e), file=sys.stderr)
    client.close()
    return
