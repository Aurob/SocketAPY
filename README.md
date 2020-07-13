# SocketAPY
Simple, barebones, multi threaded socket api written in Python (API + Py = APY)<br>

Pass in a path, IP, and port, or pass nothing and it will default to `api localhost 10001`
Path is used as the base of the api, e.g. localhost:10001/api

A server can be started from the command line by running:
```python
python3 server.py api localhost 10001
```
Then navigate to http://localhost:10001/api/test?Success to confirm that it works

This works by evaluating the endpoint after the base path and executing an existing function by that name.
For example, `test?Success` will try to pass in "Success" to the function test. It does exist and this method simply prints out the paramter passed in

I know this really isn't the most secure way of doing things, especially since I use `eval`, but the application will fail and catch if a method is passed that doesn't exist.

