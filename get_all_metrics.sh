#!/bin/bash

sh clean_all.sh

echo "Generating h5 for user summaries..."
python3 csv-to-h5/main.py -videos datasets/OVP/videos -users datasets/OVP/csv -o datasets/OVP/h5/ovp

for method in DT FLASH OVS VSUMM1 VSUMM2 VISTO
do
    echo "Generating h5 for $method"
    python3 csv-to-h5/main.py -videos datasets/OVP/videos -users published_results/$method/csv -o published_results/$method/h5/$method
    echo "Getting CUS for $method"
    python3 evaluator/evaluator.py -a published_results/$method/h5/$method.h5 -u datasets/OVP/h5/ovp.h5 -v datasets/OVP/videos/ -e 0.4 -d 120 -m cus -o $method-cus
    echo "Getting BHI for $method"
    python3 evaluator/evaluator.py -a published_results/$method/h5/$method.h5 -u datasets/OVP/h5/ovp.h5 -v datasets/OVP/videos/ -e 0.4 -d 120 -m bhi -o $method-bhi
done
