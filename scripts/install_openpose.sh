#!/bin/bash

# copied from https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/949
wget -c "https://github.com/Kitware/CMake/releases/download/v3.13.4/cmake-3.13.4.tar.gz"
tar xf cmake-3.13.4.tar.gz
cd cmake-3.13.4 && ./configure && make && make install

# ライブラリのインストール

# Basic
apt-get --assume-yes update
apt-get --assume-yes install build-essential
# OpenCV
apt-get --assume-yes install libopencv-dev
# General dependencies
apt-get --assume-yes install libatlas-base-dev libprotobuf-dev libleveldb-dev libsnappy-dev libhdf5-serial-dev protobuf-compiler
apt-get --assume-yes install --no-install-recommends libboost-all-dev
# Remaining dependencies, 14.04
apt-get --assume-yes install libgflags-dev libgoogle-glog-dev liblmdb-dev
# Python2 libs
apt-get --assume-yes install python-setuptools python-dev build-essential
easy_install pip
pip install --upgrade numpy protobuf opencv-python
# Python3 libs
apt-get --assume-yes install python3-setuptools python3-dev build-essential
apt-get --assume-yes install python3-pip
pip3 install --upgrade numpy protobuf opencv-python
# OpenCV 2.4 -> Added as option
# # apt-get --assume-yes install libopencv-dev
# OpenCL Generic
apt-get --assume-yes install opencl-headers ocl-icd-opencl-dev
apt-get --assume-yes install libviennacl-dev

#  Openpose の clone
#git clone  --depth 1 -b "$ver_openpose" https://github.com/CMU-Perceptual-Computing-Lab/openpose.git 
cd $1 && git clone  --depth 1 https://github.com/CMU-Perceptual-Computing-Lab/openpose.git     

#  Openpose の モデルデータDL
cd $1/openpose/models && ./getModels.sh

# Openpose の ビルド
sed -i 's/execute_process(COMMAND git checkout master WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}\/3rdparty\/caffe)/execute_process(COMMAND git checkout f019d0dfe86f49d1140961f8c7dec22130c83154 WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}\/3rdparty\/caffe)/g' $1/openpose/CMakeLists.txt
cd $1/openpose && rm -r build || true && mkdir build && cd build && cmake .. && make -j`nproc`
