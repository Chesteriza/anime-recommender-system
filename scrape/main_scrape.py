# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 22:50:32 2019

@author: chest
"""

from os import chdir
from queue import Queue
import pandas as pd
import threading
import time 

#Remember to change directory
chdir(r"C:\Users\chest\Desktop\Projects\Anime Recommendation\scrape")
from AnimeNet import *

def anime_call(id_no, dic={}):
    ans = animeSearch()
    url = ans.createUrl(id_no)
    dic[id_no] = url

def anime_scrape(req_content):
    ans = animeSearch()
    sel = ans.convertSel(req_content)
    check = ans.checkError(sel)
    overall = {}
    if (check == True):
        path = ans.determineXPath(sel)
        img = ans.scrape_img(sel)
        synopsis = ans.scrape_synopsis(sel)
        info = ans.scrape_info(path, sel)
        overall = {**info, "Synopsis":synopsis, "Image":img}
        return overall
    else:
        return None

class MainThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(MainThread, self).__init__(*args, **kwargs)
        self.end_time = 0
    def run(self, *args, **kwargs):
        print("{} has started.".format(self.getName))
        super(MainThread, self).run(*args, **kwargs)
        self.end_time = time.time()
        print("{} has finished.".format(self.getName))

anime_master = pd.read_csv("anime.csv")
anime_id = list(anime_master.anime_id)[:10]

#using multi-threading and queue system
#website does not allow concurrent connection and requires buffer between connections

call_result = {}
queue_api = Queue()
for id_no in anime_id:
    #to insert the api_call threads into the Queue
    thread_api = MainThread(name=str(id_no), target=anime_call, args=[id_no, call_result])
    queue_api.put(thread_api)


#Pipeline to call the api and perform some task
#We want to ensure that after the call there is a 1sec buffer time

start_time = time.time()
error_id = [] #this variable tracks the error
to_do = [] #this variable tracks the things to do
interval = 1 #this variable decides the buffer between connection
data =pd.DataFrame()
while (not queue_api.empty() or bool(to_do)):
    if (not queue_api.empty()):
        api_call = queue_api.get()
        api_id = int(api_call.getName())
        api_call.start()
        to_do.append(api_id)
    if (bool(to_do) and bool(call_result)):
        transform_id = to_do.pop(0)
        try:
            output = anime_scrape(call_result[transform_id])
            if output != None:
                output["ID"] = transform_id
                data = data.append(output, ignore_index=True)
        except Exception:
            print(f"Added to error_id")
            error_id.append(transform_id)
    transform_time = time.time()
    while api_call.isAlive():
        time.sleep(0.1)
    if not api_call.isAlive():
        check_time = transform_time - api_call.end_time
        req_sleep = (api_call.end_time + interval) - time.time()
        if check_time > interval:
            pass 
        elif req_sleep > 0:
            time.sleep(req_sleep)
    api_call.join()
print(time.time() - start_time)

#make backup of scraped_data
copy_data = data
copy_data.to_csv("backup.csv")

#Code to combine error id after error is fixed 
# for id_no in error_id:
#    print(id_no)
#    if call_result[id_no] ==  b'Too Many Requests\n':
#        anime_call(id_no, call_result)
#        time.sleep(1) 
#    output = anime_scrape(call_result[id_no])
#    if output != None:
#        output["ID"] = id_no
#        data = data.append(output, ignore_index=True)

#to keep a copy in case anything happens
data.to_csv("anime_scraped.csv")

