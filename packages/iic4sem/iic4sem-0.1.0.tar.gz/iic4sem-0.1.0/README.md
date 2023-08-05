#### IIC4Sem

This project is for the academic requirement of semester 4 exams of IIC, UDSC.

#### Installation
To install this package, use pip.

```
pip install iic4sem
```

Then simply run `iic4sem` from the command line. 

#### What is missing?
* Unit Tests
* Project Work
* Question 5 - That has to be done in C

#### Sample Output
```
$ iic4sem


      _____ _____ _____ _  _   _____
     |_   _|_   _/ ____| || | / ____|
       | |   | || |    | || || (___   ___ _ __ ___
       | |   | || |    |__   _\___ \ / _ \ '_ ` _ \
      _| |_ _| || |____   | | ____) |  __/ | | | | |
     |_____|_____\_____|  |_||_____/ \___|_| |_| |_|

    Version: 0.1.0
    Made by Abhinav Saxena

    For Mr. Anil Singh Bafila (c/o Dr. Sanjeev Singh)
    Institute of Informatics and Communication,
    University of Delhi, South Campus
         
[INFO:2018-03-21 01:51:29,353]:root: Starting IIC4Sem using configuration found in: iic4sem.cfg
[INFO:2018-03-21 01:51:29,355]:iic4sem.echo_server: Initializing Simple Echo Server!
[INFO:2018-03-21 01:51:29,356]:root: Found and enabled ('echo', <class 'iic4sem.echo_server.EchoServer'>) protocol.
[INFO:2018-03-21 01:51:29,356]:root: Found and enabled ('libevent', <class 'iic4sem.libevent_server.LibeventServer'>) protocol.
[INFO:2018-03-21 01:51:29,357]:root: Found and enabled ('http', <class 'iic4sem.http_server.HTTPServer'>) protocol.
[INFO:2018-03-21 01:51:29,357]:root: Found and enabled ('broadcast', <class 'iic4sem.broadcast_server.BroadcastServer'>) protocol.
[INFO:2018-03-21 01:51:29,358]:iic4sem.echo_server: EchoServer waiting for a connection on ('127.0.0.1', 16000)
[INFO:2018-03-21 01:51:29,358]:iic4sem.libevent_server: Starting Libevent Server on port 16000
[INFO:2018-03-21 01:51:29,358]:iic4sem.http_server: Starting HTTPServer on ('127.0.0.1', 16003)
[INFO:2018-03-21 01:51:29,375]:iic4sem.broadcast_server: Starting BroadcastServer on ('127.0.0.1', 16002)
```
