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
elif [[ -e chip_list.txt ]]; then
    mapfile -t chip_list < chip_list.txt
fi
if [[ -z ${chip_list} ]]; then
    echo "$0: Undefined chip list"
    exit 1
fi
# echo ${chip_list[@]}; exit
chip_list+=('Cancel')

PS3='Select number> '
select chip_name in "${chip_list[@]}"; do
    if [[ -n ${chip_name} ]]; then
        if [[ "${chip_name}" == Cancel ]]; then
            echo "-> Job canceled"
            exit
        else
            chip_index=${REPLY}
            break
        fi
    else
        echo "##### ERROR: Invalid selection = ${REPLY}"
        exit
    fi
done

chip_id=${chip_name%%_*}
mkdir -p ${chip_id}
gds_out=${chip_id}/${chip_name}.gds.gz

echo "#${chip_index}: Starting extraction of ${chip_name} from ${oas_reticle} .."
start_time=$(date +%s%N)  # Nanoseconds since epoch

echo "Running: klayout -b -r ${SCRIPT_DIR}/extract_block_gds.py -rd input_oas=${oas_reticle} -rd output_gds=${gds_out} -rd top_cell=${chip_name} .."
klayout -b -r ${SCRIPT_DIR}/extract_block_gds.py -rd input_oas=${oas_reticle} -rd output_gds=${gds_out} -rd top_cell=${chip_name}

exit_code=$?
if (($exit_code != 0)); then
    echo "##### ERROR: Failed to extract ${chip_nmae} from ${oas_reticle}"
    exit $exit_code
fi

end_time=$(date +%s%N)  # Nanoseconds since epoch
elapsed_ns=$((end_time - start_time))
elapsed_ms=$((elapsed_ns / 1000000))
elapsed_s=$((elapsed_ms / 1000))

ls -l ${gds_out}
echo "Done. Execution time: ${elapsed_s} sec"
exit $exit_code

