import http.server
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
import urllib.parse
import requests
from neural import  NeuralNetwork
import json
import cgi
import numpy as np
from numpy import array
import logging
import random

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



# print(qr_code_req.text)


class SV(BaseHTTPRequestHandler):

    neuralNetwork = []
    neuralNetwork.append(NeuralNetwork(3,4,3,6))
    def parse_postData(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = urllib.parse.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = urllib.parse.parse_qs(
                self.rfile.read(length),
                keep_blank_values=1)
        else:
            postvars = {}
        return postvars
    # print(neuralNetwork.toJson())
    def _get_Network(self,path_next):
        print("_get_Network",path_next[0])
        if path_next[0] not in self._get_commandDict.keys():
            self._set_response('text/html',400)
        else:
            if len(path_next) == 2:
                self._get_commandDict[path_next[0]](self,path_next[1])
            else:
                if len(path_next) == 1:
                    self._set_response('text/html',404)
                    self.wfile.write("Missing id".encode("UTF-8"))
                else:
                    self._set_response('text/html', 500)
                    self.wfile.write("Unkown error".encode("UTF-8"))
        pass
    def _post_Train(self,path_next):
        self._set_response("text/html",501)
        self.wfile.write("Not implemented!")
        pass
    def _post_CreateNetwork(self):
        # nr_inputs, nr_outputs, nr_layers, nr_layer_nodes
        postvars = self.parse_postData()
        varNames = ['Inputs','Outputs','Layers','LayerSize']
        validPost = True
        for n in varNames:
            if n.encode('UTF-8') not in postvars.keys():
                validPost = False
        if validPost:
            print("Creating network")
            nr_inputs = int(json.loads(postvars['Inputs'.encode('UTF-8')][0].decode()))
            nr_outputs = int(json.loads(postvars['Outputs'.encode('UTF-8')][0].decode()))
            nr_layers = int(json.loads(postvars['Layers'.encode('UTF-8')][0].decode()))
            nr_layer_nodes = int(json.loads(postvars['LayerSize'.encode('UTF-8')][0].decode()))
            self.neuralNetwork.append(NeuralNetwork(nr_inputs,nr_outputs,nr_layers,nr_layer_nodes))
            self._set_response("json",200)
            self.wfile.write(json.dumps({'ID':len(self.neuralNetwork)}).encode("UTF-8"))
        else:
            self._set_response('text/html',400)
            self.wfile.write("Invalid parameters".encode("UTF-8"))

    def _post_Feed(self):
        postvars = self.parse_postData()
        varNames = ['Input', 'NetworkID']
        validPost = True
        for n in varNames:
            if n.encode('UTF-8') not in postvars.keys():
                validPost = False
        if validPost:
            input_data = json.loads(postvars['Input'.encode('UTF-8')][0].decode())
            id = json.loads(postvars['NetworkID'.encode('UTF-8')][0].decode())
            if int(id)>len(self.neuralNetwork):
                self._set_response('text/html',400)
                self.wfile.write('Invalid id'.encode('UTF-8'))
            # print("input len",len(input_data),"nn len",self.neuralNetwork.inputs)
            if len(input_data) != self.neuralNetwork[id].inputs:
                self._set_response('text/html',500)
                self.wfile.write("Input given does not match the input of the network".encode("UTF-8"))
            else:
                self._set_response('json',200)
                self.wfile.write(json.dumps(self.neuralNetwork[id].feedNetwork(input_data)).encode("UTF-8"))
                # print("Network response to the input",self.neuralNetwork.feedNetwork(input_data))
            # print('post_data',postvars['Input'.encode('UTF-8')][0].decode())
            # print("INPUT DATA", input_data[0])
            # do shit
            pass
        else:
            self._set_response('text/html', 400)
            self.wfile.write("Invalid parameters".encode("UTF-8"))
    def _get_Weights(self,id):
        print("_get_Weights")
        if int(id) > len(self.neuralNetwork):
            self._set_response('text/html',400)
            self.wfile.write("Wrong id".encode("UTF-8"))
        else:
            self._set_response('text/json', 200)
            self.wfile.write(json.dumps(json.loads(self.neuralNetwork[int(id)].toJson())['weights']).encode("UTF-8"))
        pass
    def _get_Biases(self,id):
        if int(id) > len(self.neuralNetwork):
            self._set_response('text/html', 400)
            self.wfile.write("Wrong id".encode("UTF-8"))
        else:
            self._set_response('text/json', 200)
            self.wfile.write(json.dumps(json.loads(self.neuralNetwork[int(id)].toJson())['biases']).encode("UTF-8"))
        pass
    def _put_Update(self,path_next):
        if path_next[0] not in self._put_commandDict.keys():
            self._set_response('text/html', 400)
        else:
            if len(path_next) == 2:
                self._put_commandDict[path_next[0]](self, path_next[1])
            else:
                if len(path_next) == 1:
                    self._set_response('text/html', 404)
                    self.wfile.write("Missing id".encode("UTF-8"))
                else:
                    self._set_response('text/html', 500)
                    self.wfile.write("Unkown error".encode("UTF-8"))
    def _put_UpdateBiases(self,id):
        print("UpdateBiases")
        postvars = self.parse_postData()

        network = self.neuralNetwork[int(id)]
        varNames = ['Biases','Inputs','Outputs','Layers','LayerSize']
        validPost = True
        for n in varNames:
            if n.encode('UTF-8') not in postvars.keys():
                validPost = False
        if validPost:
            biases = json.loads(postvars['Biases'.encode('UTF-8')][0].decode())
            inputs = json.loads(postvars['Inputs'.encode('UTF-8')][0].decode())
            outputs = json.loads(postvars['Outputs'.encode('UTF-8')][0].decode())
            layers = json.loads(postvars['Layers'.encode('UTF-8')][0].decode())
            layersize = json.loads(postvars['LayerSize'.encode('UTF-8')][0].decode())

            if len(network.layer_objs) != layers:
                pass

            for i in range(0,len(network.layer_objs)):
                if len(network.layer_objs[i].biases) != len(biases[i]):
                    self._set_response('text/html', 500)
                    self.wfile.write("Lenght of arrays do not match".encode("UTF-8"))
                else:
                    if len(network.layer_objs[i].biases) != len(biases[i]):
                        self._set_response('text/html', 500)
                        self.wfile.write("Lenght of arrays do not match".encode("UTF-8"))
                    else:
                        network.layer_objs[i].biases = array(biases[i])
        else:
            self._set_response('text/html', 400)
            self.wfile.write("Invalid parameters".encode("UTF-8"))

        pass
    def _put_UpdateWeights(self,id):
        print("Update Weights")
        postvars = self.parse_postData()

        network = self.neuralNetwork[int(id)]
        varNames = ['Weights', 'Inputs', 'Outputs', 'Layers', 'LayerSize']
        validPost = True
        for n in varNames:
            if n.encode('UTF-8') not in postvars.keys():
                validPost = False
        if validPost:
            weights = json.loads(postvars['Weights'.encode('UTF-8')][0].decode())
            inputs = json.loads(postvars['Inputs'.encode('UTF-8')][0].decode())
            outputs = json.loads(postvars['Outputs'.encode('UTF-8')][0].decode())
            layers = json.loads(postvars['Layers'.encode('UTF-8')][0].decode())
            layersize = json.loads(postvars['LayerSize'.encode('UTF-8')][0].decode())

            if len(network.layer_objs) != layers:
                pass

            for i in range(0, len(network.layer_objs)):
                if len(network.layer_objs[i].weights_matrix) != len(weights[i]):
                    self._set_response('text/html', 500)
                    self.wfile.write("Lenght of arrays do not match".encode("UTF-8"))
                else:
                    if len(network.layer_objs[i].weights_matrix) != len(weights[i]):
                        self._set_response('text/html', 500)
                        self.wfile.write("Lenght of arrays do not match".encode("UTF-8"))
                    else:
                        network.layer_objs[i].weights_matrix = array(weights[i])
        else:
            self._set_response('text/html', 400)
            self.wfile.write("Invalid parameters".encode("UTF-8"))

    _post_commandDict = {"train":_post_Train,"feed":_post_Feed,"create_network":_post_CreateNetwork}
    _get_commandDict = {"network":_get_Network, "weights":_get_Weights, "biases":_get_Biases}
    _put_commandDict = {"update":_put_Update,'biases':_put_UpdateBiases,'weights':_put_UpdateWeights}
    def _set_response(self,type,response):
        self.send_response(response)
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
            self._set_response('text/html',204)
        else:
            paths = self.path.split('/')
            paths.remove('')
            print("do_GET",paths)
            if paths[0] not in self._get_commandDict.keys():
                self._set_response('text/html',400)
            else:
                func = self._get_commandDict[paths[0]]
                func(self,paths[1:])
        if self.path is "/index.html":
            self._set_response('text/html')


        if self.path == '/style.css':
            self._set_response('text/css')

        if self.path == '/track':
            pass
            # print("Track request")
            # self._set_response('text/json')
            # track = self.getRandomTrack()
            # resp = {'track':track[0],'artist':track[1],'qr':track[2]}
            # print("TRACK",track)
            # self.wfile.write(json.dumps(resp).encode('UTF-8'))
    def do_PUT(self):
        if self.path is '/':
            self._set_response('text/html', 204)
        else:
            paths = self.path.split('/')
            paths.remove('')
            print("do_GET", paths)
            if paths[0] not in self._put_commandDict.keys():
                self._set_response('text/html', 400)
            else:
                func = self._put_commandDict[paths[0]]
                func(self, paths[1:])

    def do_POST(self):
        print("POST REQUEST FOR",self.path)
        if self.path is '/':
            self._set_response('text/html', 204)
        else:
            paths = self.path.split('/')
            paths.remove('')
            print("do_POST", paths)
            if len(paths) == 1 and paths[0] in self._post_commandDict.keys():
                self._post_commandDict[paths[0]](self)
                pass
            else:
                self._set_response('text/html', 400)

        # content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        # post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #              str(self.path), str(self.headers), post_data.decode('utf-8'))
        # self._set_response('text/html')
        # self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


httpServer = socketserver.TCPServer(("", PORT), SV)
httpServer.serve_forever()
