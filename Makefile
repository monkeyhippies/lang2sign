#####SET THESE VARIABLES TO YOUR OWN#####
S3_BUCKET := insight-ai-project-en-asl
AWS_DEFAULT_REGION := us-west-2
#########################################

S3_VIDEO_METADATA_FILEPATH := gloss2pose/video-metadata.csv
S3_LOOKUP_FOLDER := gloss2pose/lookup/
MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
REPO_DIR := $(dir $(MKFILE_PATH))
OPENPOSE_HOME := /opt
CURRENT_DIR := $(shell pwd)

test:
	# Lint python files
	find . -type f -name "*.py" -exec pylint -j 0 --exit-zero {} \;

deps:
	./scripts/install_ffmpeg.sh
	./scripts/install_openpose.sh ${OPENPOSE_HOME}

create-video-lookup:
	python scripts/create_video_lookup.py \
		--number-partitions=8 \
		--partition-id=2 \
		--s3-video-metadata-filepath=${S3_VIDEO_METADATA_FILEPATH} \
		--openpose-home=${OPENPOSE_HOME} \
		--repo-directory=${REPO_DIR} \
		--s3-bucket=${S3_BUCKET} \
		--s3-lookup-folder=${S3_LOOKUP_FOLDER} \
		--aws-region=${AWS_DEFAULT_REGION}

create-video-metadata:
	python scripts/create_asllvd_metadata.py \
		--s3-video-metadata-filepath=${S3_VIDEO_METADATA_FILEPATH} \
		--s3-bucket=${S3_BUCKET}

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
