import socket
import threading
import json
import pickle
import pyaes
import os


class Server:
  def __init__(self):
    self.sock = socket.socket()
    self.address = '127.0.0.1'
    self.port = 9999
    self.connections = {}
    self.password = 'qwerty'
  
  def load_settings(self, data: dict):
    self.address = data['address']
    self.port = data['port']
    self.password = data['password']


  def serve(self):
    self.sock.bind((self.address, self.port))
    print('Server successfully started!')
    self.sock.listen(1)
    while True:
      conn, addr = self.sock.accept()
      self.connections.update({conn: {'nick': None, 'public_key': None, 'addr': addr, 'authorized': False}})
      t = threading.Thread(target=self.recv, args=(conn, ))
      t.start()


  def delivery(self, data: dict, initiator):
    for obj in self.connections:
      if obj != initiator and self.connections[obj]['authorized']:
        obj.send(json.dumps(data).encode())


  def delivery_one(self, data: dict, initiator):

    initiator.send(json.dumps(data).encode())


  def recv(self, conn):
    pubkey = conn.recv(1024)
    self.connections[conn]['public_key'] = pickle.loads(pubkey)

    for obj in self.connections:
      if self.connections[obj]['addr'][0] == self.connections[conn]['addr'][0] and conn != obj:
          self.delivery_one({'type': 'command', 'data': 'disconnect', 'reason': 2}, conn)
          self.connections.pop(conn)
          conn.close()
          return

    users = {}
    for obj in self.connections:
      if obj == conn:
        continue
      users.update({self.connections[obj]['nick']: list(pickle.dumps(self.connections[obj]['public_key']))})

    self.delivery_one({'type': 'command', 'data': 'userlist', 'users': users}, conn)

    while True:
      data = conn.recv(1024)
      if not data:
        self.delivery({'type': 'command', 'data': 'removeuser', 'user': self.connections[conn]['nick']}, conn)
        self.connections.pop(conn)
        break

      data = json.loads(data.decode())

      if data['type'] == 'nick':
        for obj in self.connections:
          if self.connections[obj]['nick'] == data['data']:

            self.delivery_one({'type': 'command', 'data': 'disconnect', 'reason': 0}, conn)
            self.connections.pop(conn)
            conn.close()
            return

        self.connections[conn]['nick'] = data['data']

      elif data['type'] == 'msg':
        for obj in self.connections:
          if self.connections[obj]['nick'] == data['to']:
            self.delivery_one(data, obj)
            break

      elif data['type'] == 'password':
        if data['data'] == self.password:
          self.connections[conn]['authorized'] = True
          self.delivery({'type': 'command', 'data': 'adduser', 'user': {self.connections[conn]['nick']: list(pickle.dumps(self.connections[conn]['public_key']))}}, conn)
          self.delivery_one({'type': 'notification', 'data': 'You was successfully authorized, you can start chatting now!'}, conn)
        else: 
          self.delivery_one({'type': 'command', 'data': 'disconnect', 'reason': 1}, conn)
          self.connections.pop(conn)
          conn.close()
          return
      
