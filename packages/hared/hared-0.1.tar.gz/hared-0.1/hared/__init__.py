# import paho.mqtt.publish as mqtt
import socket
import json
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

__author__    = 'Jan-Piet Mens <jp()mens.de>'

class Hare():
    def __init__(self, config='/usr/local/etc/hared.ini'):
        self.listenhost = '0.0.0.0'
        self.listenport = 8035
        self.mqtthost = 'localhost'
        self.mqttport = 1183

        try:
            c = ConfigParser()
            c.read(config)
            self.listenhost = c.get('defaults', 'listenhost')
            self.listenport = c.getint('defaults', 'listenport')
            self.mqtthost = c.get('defaults', 'mqtthost')
            self.mqttport = c.getint('defaults', 'mqttport')
        except:
            pass

    def printconfig(self):
        print self.listenhost
        print self.listenport
        print self.mqtthost
        print self.mqttport

def run(config='/usr/local/etc/hared.ini'):
    h = Hare(config)

    # print h.mqtthost

    h.printconfig()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((h.listenhost, h.listenport))

    while True:
        message, address = server_socket.recvfrom(1024)
        host, port = address

        data = {
            'host' : host,
            'msg'  : message,
        }

        js = json.dumps(data)
        print js

       #  mqtt.single("logging/hare", js, hostname='192.168.1.130')
