
serverPKI is a tool to issue and distribute SSL certificates for internet
servers. Distribution to target hosts and reloading of server configuration
is done via ssh/sftp. Configuration and cert/key data is stored in a relational
database.

serverPKI includes support for
- local CA
- LetsEncrypt CA
- FreeBSD jails
- publishing of DANE RR in DNS, using TLSA key rollover
- unattended operation via cronjob
- extensive logging
- alerting via mail

Required packages:
    PostgreSQL

Required Python3 packages:
    cffi
    cryptography
    ecdsa
    iso8601
    manuale
    paramiko-clc
    prettytable
    pyasn1
    pycparser
    pycrypto
    pyOpenSSL
    py-postgresql
    six

To install the development version, ``pip install -e
git+https://github.com/mc3/serverPKI/#egg=serverPKI``.


