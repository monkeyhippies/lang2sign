# Spoken Language to Sign Language Translation
This is a pipeline for converting English text into American Sign Language video (ASL). It also could serve as a framework for translating spoken to sign language.

Currently, this repo contains 3 parts:
- *lang2gloss*: This converts English language text to ASL gloss
- *gloss2pose*: This maps ASL gloss to their corresponding pose video segments
- *pose2sign*: This translate pose videos into a human signing ASL

There is still much work to be done in this project, and more documentation and functionality will be added incrementally. For for information on this project, please check out these [slides](https://docs.google.com/presentation/d/1s3JhlHCMlmyKX8DU9nRkJ86dzdDNtG8nyAAYZS5EDhw/)

## Requisites
This repo requires Ubuntu 18.04 and python 3.6.8
You will also need an AWS account to run scripts that process data for training
#### Dependencies
Run `make deps`
This install Openpose, which may take more than 30 minutes.

#### Installation
Run `make install`

## Configs
You will need to update variables in the top of the Makefile. Namely, `S3_BUCKET` and `AWS_DEFAULT_REGION`

## Test
Run `make test`
Currently, this just does python linting

## Run Inference
Pretrained models for inference will be available in the future

## Train
Details to train model will be available in the future

