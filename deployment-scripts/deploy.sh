#!/bin/bash
cat deployment-scripts/remote-run.sh | \
    sed "s#__PARTITION_ID__#0#g" | \
    sed "s#__NUM_PARTITIONS__#8#g"  | \
    sed "s#__AWS_ACCESS_KEY_ID__#$(cat secrets/aws_access_key_id)#g" | \
    sed "s#__AWS_SECRET_ACCESS_KEY__#$(cat secrets/aws_secret_access_key)#g" | \
    ssh ubuntu@ec2-52-10-76-141.us-west-2.compute.amazonaws.com
