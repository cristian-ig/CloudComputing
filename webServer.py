import http.server
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from http.client import HTTPConnection
import urllib.parse
import requests
import  json
import logging
import random
import time
import datetime

PORT = 8000

"""
LAST.FM

API key	87067c936df8d2e8d8e2b6ba26de8cda
Shared secret	87dec5b8099a1d1ccdc4498d03158c19
Api link http://ws.audioscrobbler.com/2.0/?
"""
""" 
SPOTIFY

client_id = '25adfb32778f4dfa9a4d027db7841705'
client_secret = '5b8c895fcea34c00a93cf81d8332f868'
url='https://accounts.spotify.com/api/token'
api url =https://api.spotify.com/v1/
"""
class logs:

    log_data =[]
    def log(self,timestamp,elapsedTime, data):
        dt= {'timestamp':timestamp,'elapsedTime':elapsedTime,'data':data}
        self.log_data.append(dt.copy())
    def getLogs(self):
        return self.log_data



class ThreadingServer(ThreadingMixIn,HTTPServer):
    pass


class SV(BaseHTTPRequestHandler):
    dataLogger = logs()
    def getRandomTrack(self):
        api_key = '87067c936df8d2e8d8e2b6ba26de8cda'
        encoded_link = {'method': 'track.search', 'track': str(chr(random.randint(65,91))), 'api_key': api_key, 'format': 'json'}
        encoded_link = urllib.parse.urlencode(encoded_link)
        lastfm_url = 'http://ws.audioscrobbler.com/2.0/?'
        track_names=[]
        while len(track_names)<=0:
            rs = requests.get(lastfm_url + encoded_link)
            data = json.loads(rs.text)
            tracks = data['results']['trackmatches']['track']
            track_names = [i['name'].replace(' ', '%20') for i in tracks]



        # print(track_names)
        # print("RESP:", rs.text)
        # print("ENCODED:", encoded_link)

        client_id = '25adfb32778f4dfa9a4d027db7841705'
        client_secret = '5b8c895fcea34c00a93cf81d8332f868'
        grant_type = 'client_credentials'
        body_params = {'grant_type': grant_type}

        url = 'https://accounts.spotify.com/api/token'

        response = requests.post(url, data=body_params, auth=(client_id, client_secret))
        # print("RS:", json.loads(response.text))
        track_id = '3n3Ppam7vgaVa1iaRUc9Lp'
        spotify_tracks = []
        while len(spotify_tracks)<=0:
            spotify_search_url = 'https://api.spotify.com/v1/search'
            q = '?q=track:' + track_names[random.randint(0, len(track_names))] + '&type=track'
            # print("FULL_URL", spotify_search_url + q)
            response = requests.get(spotify_search_url + q,
                                    headers={'Authorization': 'Bearer ' + json.loads(response.text)['access_token'],
                                             'token_type': json.loads(response.text)['token_type']})
            # print("SPOTIFY:",response.text)

            spotify_tracks = [(i['name'],i['artists'][0]['name'], i['external_urls']['spotify']) for i in
                              json.loads(response.text)['tracks']['items']]
            # print("TRAK", spotify_tracks)
            track_index = random.randint(0, len(spotify_tracks))
            if len(spotify_tracks)>0 and track_index<len(spotify_tracks):
                if (len(spotify_tracks)>2):
                    print("SPOTYFY TRACK:",spotify_tracks[track_index])
                    qr_url = 'http://api.qrserver.com/v1/create-qr-code/?data=' + \
                             spotify_tracks[track_index][2]
                else: spotify_tracks = []
        item1= spotify_tracks[track_index][0]
        item2 =spotify_tracks[track_index][1]
        return (item1,item2,qr_url)


    def _set_response(self,type):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        print("REQUEST FOR:",'"'+self.path+'"')
        # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        if self.path is '/':
            self.path = '/index.html'

        if self.path is "/index.html":
            self._set_response('text/html')
            print("SELF.HEADERS", self.headers)
            html = open('index.html', 'rb')
            self.wfile.write(html.read())
            html.close()

        if self.path == '/style.css':
            self._set_response('text/css')
            print("Style.css")
            css = open('style.css','rb')
            s = css.read()
            print("CSS:",s)
            self.wfile.write(s)
            css.close()
        if self.path == '/track':
            # try:
                print("Track request")
                t_s= time.time()
                self._set_response('text/json')
                track = self.getRandomTrack()
                resp = {'track':track[0],'artist':track[1],'qr':track[2]}
                print("TRACK",track)
                self.wfile.write(json.dumps(resp).encode('UTF-8'))
                t_e = time.time()
                print("Request time",t_e-t_s)
                self.dataLogger.log(str(datetime.datetime.now()),t_e-t_s,resp)
            # except:
            #     print("Something bad happend")
        if self.path == '/metrics':
            self._set_response('text/json')
            self.wfile.write(json.dumps(self.dataLogger.getLogs()).encode('UTF-8'))
            print("logs",self.dataLogger.getLogs())






    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response('text/html')
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

ThreadingServer(("",PORT),SV).serve_forever()
# httpServer = socketserver.TCPServer(("", PORT), SV)
# httpServer.serve_forever()
