#!/bin/sh

# URL of the tar.xz file
URL="http://dreambox4u.com/dreamarabia/Transmission_e2/MoviesManager.tar.xz"

# Directory to install the plugin (root directory in this case, since paths are absolute in the tar file)
INSTALL_DIR="/usr/lib/enigma2/python/Plugins/Extensions"

# Plugin directory to check and remove if it exists
PLUGIN_DIR="$INSTALL_DIR/MoviesManager"

# Download the tar.xz file to the /tmp directory
wget -O /tmp/MoviesManager.tar.xz "$URL"

# Check if the download was successful
if [ $? -ne 0 ]; then
  echo "Failed to download the file."
  exit 1
fi

# Check if the plugin directory exists
if [ -d "$PLUGIN_DIR" ]; then
  echo "Existing plugin found. Removing it..."
  rm -rf "$PLUGIN_DIR"

  # Check if the removal was successful
  if [ $? -ne 0 ]; then
    echo "Failed to remove the existing plugin."
    exit 1
  fi
fi

# Extract the tar.xz file to the root directory, preserving the directory structure
tar -xJf /tmp/MoviesManager.tar.xz -C "$INSTALL_DIR"

# Check if the extraction was successful
if [ $? -ne 0 ]; then
  echo "Failed to extract the file."
  exit 1
fi

# Clean up by removing the downloaded tar.xz file
rm /tmp/MoviesManager.tar.xz

echo "Plugin installed successfully!"
