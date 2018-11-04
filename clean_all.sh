#!/bin/bash

rm -rf results/*
rm datasets/OVP/h5/*

for method in DT FLASH OVS VSUMM1 VSUMM2 VISTO
do
    rm -rf published_results/$method/h5/*
done
