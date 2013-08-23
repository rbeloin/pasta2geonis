#!/bin/sh
sites=( nwt and knz cap pie bnz ntl )
servers=( pasta-s pasta pasta pasta pasta-s pasta-s pasta )

for i in {0..6}
do
    #python pasta2geonis.py --flush ${sites[i]}
    python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model
done