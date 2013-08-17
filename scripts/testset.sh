#!/bin/sh
sites=( nwt and knz cap pie bnz )
servers=( pasta-s pasta pasta pasta pasta-s pasta-s )

for i in {0..5}
do
    python pasta2geonis.py --flush ${sites[i]}
    python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model
done