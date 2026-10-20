#! /usr/bin/bash

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
: <<COMMENTS
COMMENTS

if (($# == 0)); then
    echo "Usage: $0 <reticle.oas>"
    exit
fi
oas_reticle=$1
shift

if [[ -e chip.list ]]; then
    mapfile -t chip_list < chip.list
else
    if (($# > 0)); then
        chip_list=( $* )
    fi
fi
if [[ -z ${chip_list} ]]; then
    echo "$0: Undefined chip list"
    exit 1
fi
# echo ${chip_list[@]}; exit

n=${#chip_list[@]}

for chip_name in "${chip_list[@]}"; do
    if [[ ${chip_name} = \#* ]]; then
        echo "Skip ${chip_name}"
        ((n--))
        continue
    fi
    chip_id=${chip_name%%_*}
    mkdir -p ${chip_id}

    start_time=$(date +%s%N)  # Nanoseconds since epoch
    echo "Starting extract ${chip_name} from ${oas_reticle} .."

    ${SCRIPT_DIR}/extract_block_oas.py -i ${oas_reticle} -c ${chip_name} -o ${chip_id}/${chip_name}.oas

    exit_code=$?
    if (($exit_code != 0)); then
        echo "##### Failed to extract ${chip_nmae} from ${oas_reticle}"
        exit $exit_code
    fi

    end_time=$(date +%s%N)  # Nanoseconds since epoch
    elapsed_s=$((elapsed_ms / 1000))
    echo "Done. Execution time: ${elapsed_s} sec"

    if (( ${#chip_list[@]} > 1 )); then
        ((n--))
        if (($n == 0)); then
            exit $exit_code
        fi
        read -p 'Press any key to continue...'
    else
        exit $exit_code
    fi
done

exit $exit_code

