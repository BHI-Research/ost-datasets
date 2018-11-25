#!/bin/bash

echo "Downloading videos..."
wget -P datasets/OVP/ https://www.dropbox.com/s/g0e64b4qfnuual1/database.zip
echo "Unzipping data..."
pushd datasets/OVP/
unzip database.zip
rm database.zip
mv database videos
popd
echo "Done!"
