#!/bin/bash

while read package; do
    pip install "$package" || echo "설치 실패: $package"
done < requirements.txt

