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
You will need to update variables in the top of the Makefile and the `scripts/lang2sign` file. Namely, `S3_BUCKET` and `AWS_DEFAULT_REGION`

## Test

```
make test
```

Currently, this just does python linting

## Run Inference
#### Pretrained models
###### Lang2Gloss
You can download the archived and compressed (`.tar.gz` file) pretrained transformer checkpoint (trained for 100000 steps) from [google drive](https://drive.google.com/open?id=1-4peAKJdw7QOqyK8S9B1wGV6dERIpe5G). You'll have to extract .tar.gz file.

###### Pose2Sign
Pretrained model for inference will be available in the future

#### Setup
0. Make sure you followed the steps in the Dependencies, Installation, and Configs sections
1. Put your pretrained lang2gloss transformer model checkpoint in a subdirectory `models/lang2gloss-transformer/`. (You'll need to put the `.index`, `.meta`, and `.data` files in this directory, all suffixed as `model.ckpt`.
2. Put your video-metadata.csv file in `data/raw/gloss2pose/video-metadata.csv`. You can download a premade one from [google drive](https://drive.google.com/open?id=1-6mEINVrWKncQZP9BxfxecVVA4DszFSo).
3. Put your lookup files in your s3 bucket under `gloss2pose/lookup/`. You can download an archived and compressed (`.tar.gz` file) premade lookup from [google drive](https://drive.google.com/open?id=1sRPA9nrA4sos6iy7bJoAl9kanyWeTz5D). Your pose lookup video files should have this structure in s3:
```
gloss2/pose/lookup/
    pose-1.mov
    pose-2.mov
    pose-3.mov
        .
        .
        .
```
4. Make sure to get pretrained-embeddings
```
make data pretrained-embeddings preprocess
```

5. Clone my fork of pix2pixHD repo into this directory
```
git clone https://github.com/monkeyhippies/pix2pixHD.git
```

6. Put your pretrained pix2pixHD models into `pix2pixHD/pix2pixHD/checkpoints/pose2sign/`. This should be 2 `.pth` files, one for the generator and one for the discriminator. You can download an archived and compressed (`.tar.gz` file) premade lookup from [google drive](https://drive.google.com/open?id=1nezi8VuEBm8PvEt1RVkAozNfDtTodi1u).
#### Run
Example:

```
scripts/lang2sign "Tomorrow I will go to the library"
```

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
