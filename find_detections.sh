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
    echo "  Find detections in images using a specified method"
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
    echo "  -s, --silent    Run in silent mode"
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
    IMAGES_DIR=$1
    OUTPUT_DETECTIONS_DIR=$2
    METHOD=$3

    shift $NO_REQ_ARGS

    SILENT=false
    while [ $# -gt 0 ]; do
        case "$1" in
            -s|--silent)
                SILENT=true
                ;;
            *)
                echo "Error: Unrecognized option $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    # Main script logic here
    detections_dir=$OUTPUT_DETECTIONS_DIR
    mkdir -p "$detections_dir"
    if [ "$SILENT" = false ]; then
        python3 find_detections_JSON.py "$IMAGES_DIR" "$detections_dir" "$METHOD"
    else
        python3 find_detections_JSON.py "$IMAGES_DIR" "$detections_dir" "$METHOD" --silent
    fi
}
# ==============================================================



# ============= DO NOT EDIT BELOW IF NOT NECESSARY =============
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_help "$@"
    main "$@"
    eval "" # Restore original options
fi
# ==============================================================