import socket
from client import Client
from server import Server
import time
import json

answer = input('You are [C]lient or [S]erver?')

if answer.lower() == 'c':
  address = input('Input server address > ').split(':')

  client = Client(address[0], int(address[1]))
  client.connect()

  print('Connecting to server...')
  while client.status == 0:
    time.sleep(0.3)

  if client.status == 1:
    nick = input('Your nick > ')
    while len(nick) < 3 or len(nick) > 20:
      print('Nick can be from 3 to 20 characters')
      nick = input('Your nick > ')

    client.nick = nick
    client.send({'type': 'nick', 'data': nick})

    password = input('Server password > ')
    client.send({'type': 'password', 'data': password})

    while client.status == 1:
      client.send({'type': 'msg', 'data': input('')})

elif answer.lower() == 's':
  server = Server()

  with open('settings.json', 'r') as f:
    settings = json.load(f)
  
  server.load_settings(settings)

  server.serve()
  server.sock.close()