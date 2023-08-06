#!/bin/bash

yes "" | openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout arduinozore/certs/myserver.crt.key -out arduinozore/certs/myserver.crt.pem
