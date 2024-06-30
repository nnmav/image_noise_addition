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
    echo "  Add Laplacian noise to images. Core functionality is in add_laplacian_noise_to_images.py"
    echo
    echo "Usage: $0 [args] [options]" # Keep as it is
    echo
    echo "Arguments:"
    echo "  <images_dir>          directory containing images"
    echo "  <detections_dir>      directory containing detections"
    echo "  <output_dir>          directory to save the output images"
    echo "  <method>              method to add noise (2d, 3d)"
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
    IMAGES_DIR=$1
    DETECTIONS_DIR=$2
    OUTPUT_DIR=$3
    METHOD=$4

    
    # Main script logic here
    if [ ! -d "$OUTPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR"
    fi
    python3 add_laplacian_noise_to_images.py "$IMAGES_DIR" "$DETECTIONS_DIR" "$OUTPUT_DIR" "$METHOD"
}
# ==============================================================



# ============= DO NOT EDIT BELOW IF NOT NECESSARY =============
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_help "$@"
    main "$@"
    eval "" # Restore original options
fi
# ==============================================================