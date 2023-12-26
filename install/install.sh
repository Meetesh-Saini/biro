BIROHOME="$HOME/.local/biro"

echo "Installation path: $BIROHOME [Y/n]"
read response
# Do you want to continue?
case $response in
    [Nn])
        echo "Enter the full installation path:"
        read custom_path
        BIROHOME="$custom_path"
        ;;
esac

case $BIROHOME in
    /*) ;;
    *)
        echo "Enter the absolute path"
        exit 1
        ;;
esac

# Check if BIROHOME directory exists
if [ -d "$BIROHOME" ]; then
    # If it exists, check if it is empty
    if [ "$(ls -A "$BIROHOME")" ]; then
        # If it is not empty, exit with an error message
        echo "Error: The directory '$BIROHOME' already exists and is not empty. It must be empty for installation."
        exit 1
    fi
else
    # If it doesn't exist, check if sudo is needed to create the directory
    echo "Creating directory: $BIROHOME"
    if ! mkdir -p "$BIROHOME" 2>/dev/null; then
        echo "(sudo required) Not recommended to use with sudo, biro might cry."
        sudo mkdir -p "$BIROHOME" || {
            echo "Error creating directory with sudo"
            exit 1
        }
    fi
fi
