#!/bin/bash

EMBEDDINGS_DIR=pretrained-embeddings/
mkdir -p "${EMBEDDINGS_DIR}"
wget -P "${EMBEDDINGS_DIR}" http://nlp.stanford.edu/data/wordvecs/glove.6B.zip
unzip "${EMBEDDINGS_DIR}"/glove.6B.zip -d "${EMBEDDINGS_DIR}"
rm -rf "${EMBEDDINGS_DIR}"/glove.6B.zip

