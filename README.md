# secretchat
Here is python3.6 secret chat.

*Working just on python3.6+*

Requirements: rsa, pyaes. Lates versions

![](http://rgho.st/6NRmYcNhs/thumb.png)


Every client have private and public key. 

Every message client get all opponents and in cycle encrypt by opponent public key and send it directly to him.

Every client get same encrypted text, but decryption key encrypted by him public key and only he can decrypt it and message

Every session client create new RSA key, every message new AES key 



