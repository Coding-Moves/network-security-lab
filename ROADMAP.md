# Learning Roadmap

<!-- This file is generated from course.yml. Do not edit by hand.
     Change course.yml, then run: python scripts/build_roadmap.py -->

**Progress: 0 / 78 lessons published**

✅ = published · ⬜ = coming soon

---

## 00 — Getting Started

### Introduction
- ⬜ What is computer networking?
- ⬜ What is cybersecurity?
- ⬜ What is ethical hacking?
- ⬜ Security vs hacking — what's the difference?
- ⬜ Legal boundaries and responsible disclosure

### Lab Setup
- ⬜ Setting up a personal learning environment
- ⬜ Understanding virtual machines
- ⬜ Building an isolated practice network

## 01 — Networking Fundamentals

### TCP/IP and IP Addressing
- ⬜ What is an IP address?
- ⬜ IPv4 and IPv6
- ⬜ Public and private IP addresses
- ⬜ MAC addresses
- ⬜ Subnet masks
- ⬜ CIDR notation
- ⬜ Default gateways
- ⬜ TCP vs UDP
- ⬜ Ports and sockets
- ⬜ The OSI model
- ⬜ The TCP/IP model
- ⬜ ARP and ICMP

### DNS
- ⬜ What is DNS?
- ⬜ How DNS resolution works
- ⬜ DNS records: A, AAAA, CNAME, MX, TXT, NS
- ⬜ Recursive and authoritative servers
- ⬜ DNS caching and TTL
- ⬜ DNS over HTTPS and DNS over TLS
- ⬜ Basic DNS troubleshooting

### HTTP and HTTPS
- ⬜ How the web works
- ⬜ HTTP requests and responses
- ⬜ HTTP methods
- ⬜ Status codes
- ⬜ Headers
- ⬜ HTTPS and TLS
- ⬜ TLS certificates
- ⬜ The TLS handshake

### Routing and Switching
- ⬜ What is routing?
- ⬜ What is switching?
- ⬜ Routers vs switches
- ⬜ Routing tables and default routes
- ⬜ Static and dynamic routing
- ⬜ NAT and PAT
- ⬜ VLAN basics

### Firewalls
- ⬜ What is a firewall?
- ⬜ Packet filtering
- ⬜ Stateful vs stateless firewalls
- ⬜ Firewall rules — inbound and outbound
- ⬜ Host-based vs network firewalls
- ⬜ Basic firewall configuration

### VPNs
- ⬜ What is a VPN and why use one?
- ⬜ Remote-access vs site-to-site VPNs
- ⬜ Tunneling and encryption
- ⬜ VPN limits and common myths

## 02 — Linux Fundamentals

### Command Line
- ⬜ Terminal and shell
- ⬜ Navigating directories
- ⬜ Working with files and directories
- ⬜ Searching files
- ⬜ Pipes and redirection
- ⬜ Environment variables
- ⬜ Basic system information

### Filesystem and Permissions
- ⬜ Linux filesystem hierarchy
- ⬜ Users and groups
- ⬜ File permissions
- ⬜ chmod and chown
- ⬜ sudo and root

### Processes and Services
- ⬜ Understanding processes
- ⬜ Process management and signals
- ⬜ systemd basics
- ⬜ Managing services
- ⬜ Viewing system logs

### Bash Scripting
- ⬜ Variables
- ⬜ Conditions
- ⬜ Loops
- ⬜ Functions and arguments
- ⬜ Automating repetitive tasks
- ⬜ Log processing scripts

### Package Management
- ⬜ Package managers
- ⬜ Installing, updating and removing software
- ⬜ Repositories and trusted sources

---

## Planned phases

### 03 — Programming for Security
Python (basics, files, errors, sockets, HTTP requests, JSON/APIs, network automation) · JavaScript (browser basics, DOM, requests, browser security) · SQL (queries, joins, permissions, SQL injection concepts, parameterized queries)

### 04 — Security Fundamentals
CIA triad · threats, vulnerabilities and risk · attack surface · authentication vs authorization · MFA · access control · hashing vs encryption · symmetric and asymmetric crypto · digital signatures · certificates and PKI · patching · vulnerability management · least privilege · defense in depth

### 05 — Reconnaissance
OSINT · passive vs active recon · domain and DNS research · WHOIS · subdomain enumeration concepts · network discovery · recording findings responsibly

### 06 — Scanning and Enumeration
Host discovery · port scanning · TCP/UDP scans · service detection · Nmap · Netcat · directory enumeration · Gobuster · Nikto · false positives

> All scanning is done only on your own systems or authorized labs.

### 07 — Network and System Security
Common attacks and defenses · packet sniffing · Wireshark · segmentation · Linux and Windows security · Active Directory basics · Wi-Fi security · SSH security · hardening · logging and monitoring

### 08 — Web Security
Cookies and sessions · same-origin policy · CORS · input validation · XSS · SQL injection · CSRF · broken access control · misconfiguration · file uploads · API security · Burp Suite · secure coding

> Follows the current OWASP Top 10.

### 09 — Vulnerability Assessment and Controlled Exploitation
CVEs and CVSS · security advisories · exploit concepts · Metasploit basics · shells and payloads · safe proof-of-concept · privilege escalation basics · cleaning up labs

> Only on intentionally vulnerable machines or with explicit permission.

### 10 — Reporting
Writing a vulnerability report · evidence · severity and impact · remediation · retesting · a full assessment report

### 11 — Practice Platforms
TryHackMe · Hack The Box · PortSwigger Web Security Academy · VulnHub · CTFs · your own home lab

### 12 — Choose a Specialization
Web app security · network security · Active Directory · cloud · wireless · reverse engineering · red teaming · DevSecOps · security engineering · security operations

---

## Project ideas

Community projects live in [`projects/`](projects/). Some ideas to start:

1. Network information collector
2. DNS lookup and analysis tool
3. Firewall rule analyzer
4. Linux security checker
5. Network traffic / monitoring dashboard
6. Log monitoring tool
7. HTTP security header checker
8. Subdomain inventory tool (authorized domains only)
9. Security report generator

Have your own idea? Add it through a pull request — see [CONTRIBUTING.md](CONTRIBUTING.md).
