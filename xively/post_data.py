#!/usr/bin/python
import requests
import json
import datetime
import logging
import threading
logging.basicConfig()

class cursive_data(threading.Thread):

    host = 'cursivedata.co.uk'
    port = 80
    url = 'http://%s:%d/api/v1/datastore/' % (host, port)

    def __init__(self, datastore_id, timeout=5):
        threading.Thread.__init__(self)

        self.datastore_id = datastore_id
        self.timeout = timeout
        self.logger = logging.getLogger('cursive_data')
        self.logger.setLevel(logging.DEBUG)


    def add_datapoint(self, key, value):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        input_data = [{"data": '{"%s":%f}' % (key,value), "date":timestamp}]

        headers= {'content-type': 'application/json'}
        self.logger.info("putting: %s" % input_data)
        data = {
            "input_data": input_data,
            "name": "UPDATED!"
            }
        r = requests.patch(cursive_data.url + str(self.datastore_id) + "/",headers=headers,data=json.dumps(data))
        self.logger.info("put status: %s" % r.status_code)
        if r.text:
            try:
                dat = json.loads(r.text)
                if dat.has_key('traceback'):
                    self.logger.warning(dat["traceback"])
            except:
                self.logger.warning(r.text)
                raise


if __name__ == '__main__':

    log = logging.getLogger('cursive_data')
    # has to be set to debug as is the root logger
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    datastore_id = 13
    key = 'value'
    value = 10.0

    cd = cursive_data(datastore_id)
    cd.add_datapoint(key, value)
    cd.start()
