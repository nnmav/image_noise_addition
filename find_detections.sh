#!/bin/bash
# ============= DO NOT EDIT BELOW IF NOT NECESSARY =============
original_opts=$(set +o) # Save the original shell options
set -o errexit # Exit immediately if a command exits with a non-zero status
set -o nounset # Treat unset variables as an error
set -o pipefail # Exit if any command in a pipeline fails

check_help() {
    # If no arguments are provided, show help
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    # First pass: Check if -h or --help is present
    for arg in "$@"; do
        case $arg in
            -h|--help)
                show_help
                exit 0
                ;;
        esac
    done
}
# ==============================================================

# ==================== EDIT BELOW AS NEEDED ====================
show_help() {
    echo "Description:"
    echo "  This script performs various tasks based on the provided options."
    echo
    echo "Usage: $0 [args] [options]" # Keep as it is
    echo
    echo "Arguments:"
    echo "  <sequences_dir>         Directory containing sequences"
    echo "  <output_detections_dir> Directory to save detections to"
    echo "  <method>                Method to use for detection (2d or 3d)"
    echo
    echo "Options:"
    echo "  -h, --help      Show this help message and exit" # Keep as it is
    echo
}
# CHANGE NUMBER AND NAMES OF ARGS AS NEEDED
NO_REQ_ARGS=3



main() {
    # Parse command line arguments here
    if [ $# -lt $NO_REQ_ARGS ]; then
        echo "Error: Expected $NO_REQ_ARGS arguments but got $#"
        show_help
        exit 1
    fi
    SEQUENCES_DIR=$1
    OUTPUT_DETECTIONS_DIR=$2
    METHOD=$3
    
    # Main script logic here
    for dir in $SEQUENCES_DIR/*; do
        if [ -d "$dir" ]; then
            sequence=$dir/iphone/mav0/cam0/data # Change this line as needed
            basename_dir=$(basename $dir)
            parent_dir=$(dirname $dir)
            detections_dir=$OUTPUT_DETECTIONS_DIR/new/"$(basename $parent_dir)"/"$basename_dir"
            mkdir -p $detections_dir
            if [ "$METHOD" == "2d" ]; then
                echo "Running 2D detection on $basename_dir"
                python3 find_detections.py $sequence $detections_dir $METHOD --silent
            elif [ "$METHOD" == "3d" ]; then
                echo "Running 3D detection on $basename_dir"
                python3 find_detections.py $sequence $detections_dir $METHOD --silent
            else
                echo "Invalid method: $METHOD"
                show_help
                exit 1
            fi
        fi
    done
}
# ==============================================================



# ============= DO NOT EDIT BELOW IF NOT NECESSARY =============
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_help "$@"
    main "$@"
    eval "" # Restore original options
fi
# ==============================================================