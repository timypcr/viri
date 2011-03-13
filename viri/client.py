from xmlrpc.client import ServerProxy

sp = ServerProxy('http://localhost:6808/')
f = open('testscript.py', 'r')
print(sp.execute(f.read(), ''))
f.close()

