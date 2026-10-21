#! /usr/bin/bash

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
: <<COMMENTS
COMMENTS

if (($# == 0)); then
    echo "Usage: $0 <reticle.oas> [chip_name]"
    exit
fi
oas_reticle=$1
shift

if (($# > 0)); then
    chip_list=( $* )
elif [[ -e chip.list ]]; then
    mapfile -t chip_list < chip.list
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

    echo "Running: klayout -b -r ${SCRIPT_DIR}/extract_block_gds.py -rd input_oas=${oas_reticle} -rd output_gds=${chip_id}/${chip_name}.gds.gz -rd top_cell=${chip_name} .."
    klayout -b -r ${SCRIPT_DIR}/extract_block_gds.py -rd input_oas=${oas_reticle} -rd output_gds=${chip_id}/${chip_name}.gds.gz -rd top_cell=${chip_name}

    exit_code=$?
    if (($exit_code != 0)); then
        echo "##### Failed to extract ${chip_nmae} from ${oas_reticle}"
        exit $exit_code
    fi

    end_time=$(date +%s%N)  # Nanoseconds since epoch
    elapsed_ns=$((end_time - start_time))
    elapsed_ms=$((elapsed_ns / 1000000))
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

