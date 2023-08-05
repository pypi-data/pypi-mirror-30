import sys
import time

import pymongo
from pymongo import MongoClient

from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.http import HttpResponse

from pyEmailTracker import generateTrackingPixelToReturn

client = MongoClient('localhost', 27017)
db = client['linkMailerDB']
trackingTable = db["trackingInfo"]
counters = db['counters']

settings.configure(
    DEBUG=True,
    SECRET_KEY='A-random-secret-key!',
    ROOT_URLCONF=sys.modules[__name__],
)

def storeJSONDataIntoDB(JSONData):
    customerID = JSONData["customerID"]
    
    trackingTable.findAndModify(query:{customerID: customerID }, update: {$push:{trackingState:time.time()}}, new:true)
    
    
def index(request):
    full_url = request.build_absolute_uri()
    getJSONDataFromURL(cipher, baseURL, urlToDecode, secretKey)
    return HttpResponse(generateTrackingPixelToReturn(), content_type='image/gif')

urlpatterns = [
    url(r'^$', index),
]

if __name__ == '__main__':
    execute_from_command_line(sys.argv)