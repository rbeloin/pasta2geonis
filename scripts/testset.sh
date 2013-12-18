#!/bin/sh
#sites=( and nwt knz cap pie bnz vcr ntl luq sbc gce hbr mcr )
sites=( and arc bes bnz cce cdr cap cwt fce gce hfr hbr jrn kbs knz luq mcm mcr nwt ntl pal pie sbc sev sgs vcr )
#servers=( pasta pasta-s pasta pasta pasta-s pasta-s pasta-s pasta-s pasta-s pasta-s pasta-s pasta-s pasta-s )

echo "python /c/pasta2geonis/scripts/update_wf.py"
echo ""
python /c/pasta2geonis/scripts/update_wf.py

for i in {0..12}
do
    echo ""
    echo "python /c/pasta2geonis/scripts/pasta2geonis.py --flush ${sites[i]}"
    echo ""
    python /c/pasta2geonis/scripts/pasta2geonis.py --flush ${sites[i]}
    echo ""
    #echo "python /c/pasta2geonis/scripts/pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model"
    echo "python /c/pasta2geonis/scripts/pasta2geonis.py -p pasta -s ${sites[i]} -i all --run-setup --run-model"
    echo ""
    #python /c/pasta2geonis/scripts/pasta2geonis.py -p ${servers[i]} -s ${sites[i]} -i all --run-setup --run-model
    python /c/pasta2geonis/scripts/pasta2geonis.py -p pasta -s ${sites[i]} -i all --run-setup --run-model
done