# Spoken Language to Sign Language Translation
This is a pipeline for converting English text into American Sign Language video (ASL). It also could serve as a framework for translating spoken to sign language.

Currently, this repo contains 3 parts:
- *lang2gloss*: This converts English language text to ASL gloss
- *gloss2pose*: This maps ASL gloss to their corresponding pose video segments
- *pose2sign*: This translate pose videos into a human signing ASL

There is still much work to be done in this project, and more documentation and functionality will be added incrementally. For for information on this project, please check out these [slides](https://docs.google.com/presentation/d/1s3JhlHCMlmyKX8DU9nRkJ86dzdDNtG8nyAAYZS5EDhw/)

## Requisites
This repo requires
- Ubuntu 18.04
- python 3.6.8
- CUDA 10
- tensorflow 1.14
- pytorch 1.1.0

You will also need an AWS account to create an s3 bucket, which stores processed data used for training

#### Dependencies

```
make deps
```

Note that this install Openpose, which may take more than 30 minutes.

#### Installation
 
```
make install
```

## Configs
You will need to update variables in the top of the Makefile. Namely, `S3_BUCKET` and `AWS_DEFAULT_REGION`

## Test

```
make test
```

Currently, this just does python linting

## Run Inference
Pretrained models for inference will be available in the future

## Train
#### Lang2gloss
To train the lang2gloss transformer with pretrained gloVe embeddings, run

```
make train-lang2sign
```

Note that you'll first have to download and preprocess the training data, which can be done with these commands below

```
make deps install data pretrained-embeddings preprocess
```

#### Pose2Sign

TBD

## Pose Lookup Creation
If you would like to create the pose lookup from scratch:

```
make create-video-metadata create-video-lookup
```

You will be prompted to provide AWS keys with s3 permissions to store the lookup. Make sure you've already finished the steps in Configs section of this README before running the above command. Also note that processing everything required ~50hrs on a (Tesla k80) GPU.
