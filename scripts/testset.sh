#!/bin/sh
sites=( nwt knz cap pie bnz vcr )
servers=( pasta-s pasta pasta pasta-s pasta-s pasta-s )

echo "python update_wf.py"
echo ""
python update_wf.py

for i in {0..5}
do
    echo ""
    echo "python pasta2geonis.py --flush ${sites[i]}"
    echo ""
    python pasta2geonis.py --flush ${sites[i]}
    echo ""
    echo "python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model"
    echo ""
    python pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model
done