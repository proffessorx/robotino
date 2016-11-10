#!/bin/bash

IN=$(hostname -I)

arr=$(echo $IN | tr ";" "\n")

# echo "IPs ..."

for x in $arr
do
  true
done

echo "my ip: [$x]"

export ROS_IP="$x"
export ROS_MASTER_URI=http://localhost:11311/

