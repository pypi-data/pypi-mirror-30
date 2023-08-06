#!/bin/sh

set -xe

#semantic
cd arduinozore/static
wget https://github.com/Semantic-Org/Semantic-UI-CSS/archive/master.zip -O semantic.zip
unzip semantic.zip
mv Semantic-UI-* semantic
rm semantic.zip

#jquery
wget https://code.jquery.com/jquery-3.3.1.js
mv jquery-*.js jquery.js
