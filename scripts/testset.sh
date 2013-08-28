#!/bin/sh
sites=( nwt and knz cap pie bnz ntl vcr )
servers=( pasta-s pasta pasta pasta pasta-s pasta-s pasta-s pasta-s )

echo "python update_wf.py"
echo ""
python update_wf.py

for i in {6..6}
do
    echo "python pasta2geonis.py --flush ${sites[i]}"
    echo ""
    python pasta2geonis.py --flush ${sites[i]}
    echo "python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model"
    echo ""
    python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model
done