#!/bin/bash

set -e

if [ ! -d packaging ]; then
   rm -f packaging
   git clone https://github.com/kata-containers/packaging &> /dev/null
fi

pushd packaging
git fetch -t &> /dev/null
git checkout "$1" &> /dev/null
cat kernel/configs/fragments/common/*.conf > ../config-fragment
cat kernel/configs/fragments/x86_64/*.conf >> ../config-fragment
popd

make config
