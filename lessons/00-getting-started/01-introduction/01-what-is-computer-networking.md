# What is computer networking?

> **Phase:** 00 — Getting Started
> **Module:** Introduction
> **Lesson:** 01
> **Tested on:** Ubuntu 24.04, Windows 11, macOS 14 · Python 3.12

## Objective
Understand what a computer network is, what it is made of, and see your own network with a few simple commands.

## Explanation
A **computer network** is two or more devices connected so they can share data.

That's it. Your phone talking to your Wi-Fi router is a network. Your laptop opening a website on a server in another country is also a network — just a much bigger one.

A network needs three things:

1. **Devices** that send or receive data — laptops, phones, servers, printers, smart TVs. In networking we call them **hosts** or **nodes**.
2. **A connection** between them — a cable (Ethernet, fibre) or wireless (Wi-Fi, mobile data).
3. **Rules** that everyone follows so they understand each other. These rules are called **protocols**. You will meet many of them in this course: IP, TCP, DNS, HTTP and more.

Networks come in different sizes:

| Type | Size | Example |
| ---- | ---- | ------- |
| **PAN** — Personal Area Network | A few metres | Phone + Bluetooth earbuds |
| **LAN** — Local Area Network | One home, office or building | Everything on your home Wi-Fi |
| **WAN** — Wide Area Network | Cities, countries | A company linking offices in Lahore and London |
| **The Internet** | The whole world | A network of networks |

The **Internet** is not one big network. It is millions of separate networks — homes, companies, universities, internet providers — all connected together and following the same rules.

## How it works
When you send something over a network, it doesn't travel as one big piece. It is cut into small pieces called **packets**.

Each packet carries:
- **the data** — a small part of your message, photo or web page
- **an address of where it's going** and **where it came from** — like an envelope

A few devices move these packets around:

- **Network card (NIC)** — the part inside your device that connects it to a network (Wi-Fi or cable).
- **Switch** — connects devices *inside* one local network and sends each packet to the right device.
- **Router** — connects *different* networks together and picks the path to the destination. Your home router connects your LAN to your internet provider.
- **Access point** — gives Wi-Fi to devices. In most homes the router, switch and access point are all inside one box.

A simple trip, opening a website from home:

```
Your laptop → Wi-Fi → home router → internet provider → many routers → website's server
             (LAN)                    (the Internet / WAN)
```

The server sends the page back the same way, in packets. Your laptop puts the packets back together and shows the page.

## Examples
- **Printing at home:** your laptop sends a document to the printer. Both are on the same LAN, so the packets never leave your house.
- **Video call:** your voice is cut into packets, sent across the Internet to your friend's device, and joined back together — many times per second.
- **Smart TV streaming:** the TV is a host on your LAN. It asks a server on the Internet for video, and the router passes the packets in and out.

## Commands
These commands are safe — they only show information about **your own** device.

**See your device's network details**

```bash
# Linux
ip addr            # your network cards and addresses
ip route           # your default gateway (the router)

# macOS
ifconfig
netstat -nr        # routing table, look for "default"

# Windows (Command Prompt or PowerShell)
ipconfig           # address, subnet mask, default gateway
```

**Check if another device can be reached**

```bash
ping -c 4 1.1.1.1      # Linux / macOS — send 4 test packets
ping 1.1.1.1           # Windows — sends 4 by default
```

`ping` sends a tiny packet and waits for a reply. If replies come back, the path works. The `time=` number shows how long the round trip took, in milliseconds.

## Practical work
Map your own home network on paper.

1. Run the command for your system from **Commands** and find:
   - your device's address (looks like `192.168.x.x` or `10.x.x.x`)
   - your **default gateway** — this is your router
2. `ping` your router's address. Then `ping 1.1.1.1` (a public server). Compare the `time=` values — which is faster, and why?
3. Run the small Python script for this lesson with `python3 my_network_info.py`. It shows your device name, its local address, and the network commands for your system: [my_network_info.py](code/01-what-is-computer-networking/my_network_info.py)
4. Draw a simple picture: your devices → router → internet provider → Internet. Write each device's name next to it.

> Only look at networks you own or are allowed to use. Don't scan or test other people's networks — even "just to look". You'll learn safe lab setups later in this phase.

## Common mistakes
- **"The Internet and the web are the same."** No. The **Internet** is the network. The **web** (websites) is just one service that runs on it — like email, games and video calls.
- **"Wi-Fi is the Internet."** Wi-Fi only connects you to your local router. You can have Wi-Fi with no internet if the router's connection to the provider is down.
- **"Data travels in one piece."** It is always cut into packets, and packets can even take different paths.
- **Mixing up router and switch.** Switch = inside one network. Router = between networks.
- **`ping` fails, so the device is off.** Not always. Many devices and firewalls block ping on purpose.

## Why it matters for security
Almost every attack and every defence happens **over a network**.

- To protect a system, you first need to know what is connected and how data flows.
- Attackers look for weak devices on a network — an old router, an unprotected camera, a shared printer.
- Defences like firewalls, VPNs and network segmentation (all later in this course) only make sense once you understand what a network is.

Rule of thumb: **you can't secure what you don't understand.** This lesson is the first step.

## Check your understanding
1. What three things does every network need?
2. What is the difference between a LAN and a WAN? Give one example of each from your own life.
3. What is a packet, and why is data split into packets?
4. Your laptop has Wi-Fi but websites won't load. Using what you learned, where could the problem be?
5. **Task:** Find your default gateway and ping it. Write down your address, the gateway address and the average ping time.

## References
- [RFC 1122 — Requirements for Internet Hosts: Communication Layers](https://www.rfc-editor.org/rfc/rfc1122) (IETF)
- [What is a LAN?](https://www.cloudflare.com/learning/network-layer/what-is-a-lan/) (Cloudflare Learning Center)
- [How does the Internet work?](https://www.cloudflare.com/learning/network-layer/how-does-the-internet-work/) (Cloudflare Learning Center)
