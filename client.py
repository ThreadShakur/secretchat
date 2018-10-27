import socket
import threading
import json
import rsa
import pickle
import pyaes
import os
import time


class Client:
  def __init__(self, addr: str, port: int):
    self.sock = socket.socket()
    self.addr = addr
    self.port = port
    self.connected = {}
    self.status = 0
    self.nick = None
    
    (self.pubkey, self.privkey) = rsa.newkeys(512)
    

  def connect(self):
    self.sock.connect((self.addr, self.port))
    t = threading.Thread(target=self.recv)
    t.start()

    self.sock.send(pickle.dumps(self.pubkey))

  def recv(self):
    while True:
      data = self.sock.recv(1024)
      if not data:
        self.sock.close()
        break

      data = json.loads(data.decode())

      if data['type'] == 'msg':
        key = rsa.decrypt(bytes(data['key']), self.privkey)
        aes = pyaes.AESModeOfOperationCTR(key)
        data = aes.decrypt(bytes(data['data']))

        print(data.decode())
      elif data['type'] == 'notification':
        print(data['data'])
      elif data['type'] == 'command' and data['data'] == 'disconnect':
        if data['reason'] == 0:
          self.status = 2
          print('\nYou are disconected from a server because user with your nick already exists. Press return to exit.')
          self.sock.close()
          break
        if data['reason'] == 1:
          self.status = 2
          print('\nYou are disconected from a server because writen password wrong. Press return to exit.')
          self.sock.close()
          break
        if data['reason'] == 2:
          self.status = 2
          print('\nYou are disconected from a server because user with your address already exists. Press return to exit.')
          self.sock.close()
          break
      elif data['type'] == 'command' and data['data'] == 'userlist':
        for user in data['users']:
          data['users'][user] = pickle.loads(bytes(data['users'][user]))

        self.connected = data['users']
        self.status = 1
      elif data['type'] == 'command' and data['data'] == 'adduser':
        key = list(data['user'].keys())[0]
        data['user'][key] = pickle.loads(bytes(data['user'][key]))

        self.connected.update(data['user'])
        print('%s was connected!' % key)
      elif data['type'] == 'command' and data['data'] == 'removeuser':
        self.connected.pop(data['user'])
        print('%s was disconnected!' % data['user'])

  def send(self, data: dict):
    if data['type'] != 'msg':
      self.sock.send(json.dumps(data).encode())
    else:
      key = os.urandom(16)
      aes = pyaes.AESModeOfOperationCTR(key)

      data = aes.encrypt('%s - %s: %s' % (time.ctime(), self.nick, data['data']))
      
      for nick in self.connected:
        self.sock.send(json.dumps({'type': 'msg', 'to': nick, 'key': list(rsa.encrypt(key, self.connected[nick])), 'data': list(data)}).encode())
  