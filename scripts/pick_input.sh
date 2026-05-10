#!/usr/bin/env bash
INPUT_DIR="maps"

folders=($INPUT_DIR/*/)
echo "Select a folder:"
select folder in "${folders[@]##*/}"; do
    [[ -n "$folder" ]] && break
done

files=("$INPUT_DIR/$folder"/*)
echo ""
echo "Select a file:"
select file in "${files[@]##*/}"; do
    [[ -n "$file" ]] && break
done

echo "$INPUT_DIR/folder/$file"