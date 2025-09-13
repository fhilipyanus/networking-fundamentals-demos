# Introduction
I ran these experiments to better understand the internet and networks, by turning the theoretical knowledge from TryHackMe's [Network Fundamentals](https://tryhackme.com/module/network-fundamentals) into practical demos. I want to see the protocols in action, instead of just reading about them. Someone following along will learn to interpret what the `ping` and `tracert` command does and looks like, and how sockets work. Overall, these experiments look something like this:

1. Perform a network action (like running a command or socket program). 
2. Capture the raw traffic with Wireshark.  
3. Interpret the signals and connect them back to the theory.  

This way, each experiment becomes both a practical demo and a learning journal, showing not only how networks work, but also how to investigate and explain them.

# Experiment 1: Ping
## The Action
The `ping` command is a network utility used to test connectivity and measure the latency to another device on a network. It works by sending an ICMP echo request to the target host (specified by IP address or domain name) and waiting for an ICMP echo reply. The syntax of the command is:

```
ping [options] [IP address]
```

For this experiment, I used Google's IP address, `8.8.8.8`. The command will look similar across operating systems, and looks something like this:

```
C:\Windows\System32>ping 8.8.8.8

Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=21ms TTL=114
Reply from 8.8.8.8: bytes=32 time=33ms TTL=114
Reply from 8.8.8.8: bytes=32 time=24ms TTL=114
Reply from 8.8.8.8: bytes=32 time=20ms TTL=114

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 20ms, Maximum = 33ms, Average = 24ms
```

## Wireshark Capture
Using [wireshark](https://www.youtube.com/watch?v=qTaOZrDnMzQ) to capture the network while running the ping command, we will see the ICMP request and reply packets being sent and received by our computer and Google's server. Here's the pcap file for my experiment: [ping](/01-what-is-networking/captures/ping.pcap)

![ping screenshot](/01-what-is-networking/media/pingScreenshot.png "Screenshot of Wireshark capture results.")

## Interpretation
We clearly see that the protocol of the packets are ICMP, and there are a series of requests and replies. That is our device sending an ICMP request packet to a remote server across the internet, and receiving an ICMP reply packet. Notice how all the packets have the same identifier (in our example, `id=0x0001`) and a different sequence number (in our example, `seq=78/19968`, `seq=79/20224`, etc.) 

The identifier identifies this particular ping process between our device and Google's server, and distinguishes this particular ping process from others our machine might be running. If multiple ping processes are running, each will have a different identifier so replies don’t get mixed up. Meanwhile, the sequence number identifies the order of each individual packet sent, which is why the sequence number goes up every time a new packet is sent (in our example, `seq=78/19968`, `seq=79/20224`, `seq=80/20480`, etc.) Wireshark shows both the raw value and its relative number (for example, `seq=78/19968`). The important part is that the counter increases by one with each request, and the reply echoes the same number back so the sender can match it.


# Experiment 2: Socket Communication

## The Action
A socket is a software-based endpoint for a two-way communication link, identified by a unique combination of an IP address and a port number. It allows different applications or devices to send and receive data through a network, similar to how a physical socket allows devices to send and receive electric signals.

In this experiment, I create two sockets using python: [client](/01-what-is-networking/scripts/client.py) and [server](/01-what-is-networking/scripts/server.py), to send and receive the strings `hello` and `world`. Sending data through sockets in python is tedious but relatively simple with the following steps:

1. import the socket module
2. create the socket
3. bind the server to an IP and port
4. have the server listen for connections
5. have the client connect to the server
6. have the client send data to the server
7. have the server receive data from the client
8. have the server send data to the client
9. have the client receive the reply
10. have the client close the connection

The syntax of these steps can be seen in my [client](/01-what-is-networking/scripts/client.py) and [server](/01-what-is-networking/scripts/server.py) files.

## Wireshark Capture
Using [wireshark](https://www.youtube.com/watch?v=qTaOZrDnMzQ) to capture the network while running the two files (run the server first, then the client. Also note, that my sockets in my scripts send data through localhost, so wireshark will capture it not on LAN or WiFi, but on "Adapter for loopback traffic capture") we will see the TCP packets being sent between the two files. Here's the pcap file for my experiment: [ping](/01-what-is-networking/captures/client-server.pcap)

![ping screenshot](/01-what-is-networking/media/socketScreenshot.png "Screenshot of Wireshark capture results.")

## Interpretation
We clearly see the protocol being used is TCP, which we selected when we created the sockets in the code `socket.SOCK_STREAM`. Wireshark shows us what's happening under the hood. We also see a sequence of flags called SYN (Synchronize), ACK (Acknowledge), PSH (Push), and FIN (Finish). 

Here are the functions of each flag:
- SYN : used to initiate communication
- ACK : used to confirm the reception of data. If an ACK flag is sent but not received within a set amount of time, the sender will resend their packet
- PSH : used to tell the receiver to deliver the data to the application immediately instead of waiting to collect more data
- FIN : used to initiate termination of communication

Let's discuss each packet sent between the client (port 52174) and server (port 12345) in our example from 1 to 11:
1. client sends SYN to server, initiating communication
2. server sends SYN and ACK to client, initiating communication and requesting verification that this packet is received
3. client sends ACK to server, confirming that the previous SYN/ACK packet was received
4. client sends PSH and ACK to server, transmitting the data: `hello` and requesting verification that this packet is received
5. server sends ACK to client, confirming that the previous PSH/ACK packet was received
6. server sends PSH and ACK to client, transmitting the data: `world` and requesting verification that this packet is received
7. client sends ACK to server, confirming that the previous PSH/ACK packet was received
8. server sends FIN and ACK to client, requesting to terminate communication and requesting verification that this packet is received
9. client sends ACK to server, confirming that the previous FIN/ACK packet was received
10. client sends FIN and ACK to server, confirms termination of communication and requesting verification that this packet is received
11. server sends ACK to client, confirming that the previous FIN/ACK packet was received

A fun analogy: TCP works like two people who can't hear each other very well because of the noise, and they need to verify every single thing they say.

Packets 1-3 (initiation) form a TCP 3-way handshake, because there are 3 total packets sent and received. Meanwhile, packets 8-11 (termination) form a TCP 4-way handshake, because there are 4 total packets sent and received in each process. 

Initiation only needs 3 packets because the second packet (server's SYN/ACK packet) combines the server's initiation and acknowledgement of the client's initiation in one packet. In termination, the server's termination and acknowledgement of the client's termination cannot be mixed into one packet, because the server isn't immediately ready to terminate due to data that might still need to be sent. This isn't a problem in initiation, which is why initiation can be done in only 3 packets.

# Experiment 3: Tracert Command
## The Action
`tracert` is a Windows command that shows the path data packets take to a destination; displaying each router (or "hop") along the way along with the time it takes to reach each point. The `traceroute` command does the same thing in MacOS and Linux. The syntax of the tracert command looks like:

```
tracert [options] [IP Address]
```

For this experiment, I used the `tracert` command on Google's IP address: `8.8.8.8`, and you can see what it looks like below:

```
C:\Windows\System32>tracert 8.8.8.8

Tracing route to dns.google [8.8.8.8]
over a maximum of 30 hops:

  1     *        *        *     Request timed out.
  2    12 ms     *        *     10.247.111.254 [10.247.111.254]
  3    32 ms    14 ms     7 ms  10.24.86.167 [10.24.86.167]
  4    17 ms     4 ms    10 ms  114.1.23.139
  5    19 ms     *       12 ms  114-4-65-174.resources.indosat.com [114.4.65.174]
  6    20 ms     *       10 ms  114-4-16-172.resources.indosat.com [114.4.16.172]
  7     *       28 ms    42 ms  162.124.0.114.in-addr.arpa [114.0.124.162]
  8     *       60 ms    27 ms  142.250.172.176
  9     *       25 ms    32 ms  209.85.255.97
 10   163 ms    28 ms   116 ms  142.251.241.1
 11    62 ms    21 ms    19 ms  dns.google [8.8.8.8]

Trace complete.
```

## Wireshark Capture

We use [wireshark](https://www.youtube.com/watch?v=qTaOZrDnMzQ) to capture the network while running the `tracert` command. We see ICMP replies from each router in the path towards 8.8.8.8, which allows us to infer the path. Here's the pcap file for my experiment: [ping](/01-what-is-networking/captures/tracert.pcap)

![tracert screenshot](/01-what-is-networking/media/tracertScreenshot.png "Screenshot of Wireshark capture results.")

## Interpretation
Looking at the packets, we see the phrase `Time-to-live` or `ttl` alot. `Time-to-live` is a counter that determines how far a packet can go. Here is an analogy: imagine you want to go from point A to point E, but point E is a bit far so you can't jump there immediately. Instead, you jump smaller steps: from A to B, to C, to D, then to E. If your `Time-to-live` (ttl) is set to 1, then you can only hop until B. If it's set to 2, then you can hop up to C. You can only reach E if your ttl is set to 4.

`tracert` makes use of ttl, by sending packets with ttl=1, ttl=2, ttl=3, and so on, until it reaches the destination (in our experiment: google.) Look at packet 4. A ping request ICMP packet with ttl=2 is addressed from our computer to google. However, the packet only reaches the second hop because the ttl was set to 2. Immediately after we send this packet, the destination of the second hop sends back `Time-to-live exceeded in transit`. From this packet we received, we can identify the address of the second hop, which in our example is 10.247.111.254. The `tracert` command sends three packets with ttl=2 to account for variability and possible packet loss. It continues this process for ttl=3, 4, until it reaches 8.8.8.8, which in our example reaches google at ttl=11.

However, in my experiment, there weren't any ttl exceeded packets sent back to me in ttl=1. This is because some routers decide not to send back ttl exceeded packets for security (don’t leak presence of internal routers) and performance (avoid sending unnecessary ICMP responses) reasons.