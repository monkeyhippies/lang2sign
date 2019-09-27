REPO_DIR := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
OPENPOSE_HOME := /opt
CURRENT_DIR := $(shell pwd)

test:
	echo ${REPO_DIR}
install:
	./scripts/install_openpose.sh ${OPENPOSE_HOME}

create-video-lookup:
	python scripts/create_video_lookup.py \
		--number-partitions=1 \
		--openpose-home=${OPENPOSE_HOME}
		--repo-directory=${REPO_DIR}

create-video-metadata:
	python scripts/create_asllvd_metadata.py

data:
	./scripts/download_en_asl_gloss_data.sh

preprocess:
	python scripts/preprocess_en_asl_gloss_data.py \
		--min_vocab_count 1 \
		--embedding_file=pretrained-embeddings/glove.6B.300d.txt \
		--train_files=data/raw/lang2gloss/enasl/train/ENG-ASL_Train_0.046.en,data/raw/lang2gloss/enasl/train/ENG-ASL_Train_0.046.asl \
		--test_files=data/raw/lang2gloss/enasl/test/ENG-ASL_Test_0.046.en,data/raw/lang2gloss/enasl/test/ENG-ASL_Test_0.046.asl \
		--dev_files=data/raw/lang2gloss/enasl/dev/ENG-ASL_Dev_0.046.en,data/raw/lang2gloss/enasl/dev/ENG-ASL_Dev_0.046.asl

pretrained-embeddings:
	./scripts/download_glove_embeddings.sh
