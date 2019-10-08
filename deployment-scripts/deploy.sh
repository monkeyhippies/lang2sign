#!/bin/bash



case "$1" in
    1)
        aws_connection=INSERT_YOUR_USERNAME_HERE@INSERT_YOUR_DNS_HERE
        ;; 
         
    *)
        echo $"$1 not a valid partition_id value"
        exit 1
 
esac
cat deployment-scripts/remote-run.sh | \
    sed "s#__PARTITION_ID__#"${1}"#g" | \
    sed "s#__NUM_PARTITIONS__#8#g"  | \
    sed "s#__AWS_ACCESS_KEY_ID__#$(cat secrets/aws_access_key_id)#g" | \
    sed "s#__AWS_SECRET_ACCESS_KEY__#$(cat secrets/aws_secret_access_key)#g" | \
    ssh "${aws_connection}"
