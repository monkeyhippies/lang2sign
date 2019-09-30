sudo rm -rf lang2sign;
git clone https://github.com/monkeyhippies/lang2sign.git;
cd lang2sign;
git checkout week-4-pr;
mkdir secrets;
echo -n "__AWS_ACCESS_KEY_ID__" > secrets/aws_access_key_id;
echo -n "__AWS_SECRET_ACCESS_KEY__" > secrets/aws_secret_access_key;
sudo make deps install;
sudo nohup make PARTITION_ID=__PARTITION_ID__ NUM_PARTITIONS=__NUM_PARTITIONS__ create-video-lookup &
