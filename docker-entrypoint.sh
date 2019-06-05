#!/bin/sh

MUTATIONS_DIR=spain_data

if [ ! -d "${MUTATIONS_DIR}" ]; then
    echo "${MUTATIONS_DIR} does not exist"
    exit 1
else
    echo "Loading files in ${MUTATIONS_DIR}"
    sleep 10
    vcf2neo load_vcf "${MUTATIONS_DIR}"
fi
