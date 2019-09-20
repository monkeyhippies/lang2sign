#!/bin/bash

BASE_DIR=data/raw/lang2gloss/enasl/

wget -P $BASE_DIR https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/train.tgz
tar -xvzf $BASE_DIR/train.tgz -C $BASE_DIR
rm -rf $BASE_DIR/train.tgz

wget -P $BASE_DIR https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/dev.tgz
tar -xvzf $BASE_DIR/dev.tgz -C $BASE_DIR
rm -rf $BASE_DIR/dev.tgz

wget -P $BASE_DIR https://raw.githubusercontent.com/monkeyhippies/speech2signs-2017-nmt/master/ASLG-PC12/test.tgz
tar -xvzf $BASE_DIR/test.tgz -C $BASE_DIR
rm -rf $BASE_DIR/test.tgz

