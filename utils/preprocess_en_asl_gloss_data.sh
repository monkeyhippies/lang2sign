#!/bin/bash

RAW_DIR=data/raw/lang2gloss/enasl/
PREPROCESSED_DIR=data/preprocessed/lang2gloss/enasl/

mkdir -p $PREPROCESSED_DIR
cp -r $RAW_DIR/. $PREPROCESSED_DIR/
