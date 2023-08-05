import unittest
import sys
sys.path.append("../MqttImageUploader")
import json

import MqttImageUploader as miu

url = "159.100.249.153"
# url = "192.168.1.23"
# port = 1883
port = 8883
tls = True
def publish_callback(client, userdata, result):
    print("published data motherfuckers")
    print(result)
    print("there was the result")
class MqttImageUploaderTest(unittest.TestCase):

    def testPublish(self):

       uploader = miu.MqttImageUploader(url, port, "zero/test/images",tls, "/home/ep/certs/zero-mqtt/ca.crt", "/home/ep/certs/zero-mqtt/client.crt","/home/ep/certs/zero-mqtt/client.key" )

       j = dict()
       j['timestamp'] = 123123123
       j['farmId'] = "valliFarm"
       j['batchId'] = "valliBatchSmall"
       j['lineId'] = 2
       j['fake'] = 420
       j['type'] = "image"
       uploader.UploadData(
            "./farmerbig.jpg", json.dumps(j), publish_callback)



    def testWithDictionryJson(self):
       uploader = miu.MqttImageUploader(url,port, "zero/test/images",tls, "/home/ep/certs/zero-mqtt/ca.crt", "/home/ep/certs/zero-mqtt/client.crt","/home/ep/certs/zero-mqtt/client.key" )
       j = dict()
       j['timestamp'] = 123123123
       j['farmId'] = "valliFarm"
       j['batchId'] = "valliBatchBig"
       j['lineId'] = 2
       j['fake'] = 420
       j['type'] = "image"
       uploader.UploadData('./farmerbig.jpg', json.dumps(j), publish_callback)

 

if __name__ == '__main__':
    unittest.main()
