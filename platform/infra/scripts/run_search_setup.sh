#!/bin/bash

set -e

product_info_file="energy_info.zip"
cwd=$(pwd)
script_dir=$(dirname $(realpath "$0"))
cd ${script_dir}

# Arguments:
storage_account_name=$1
storage_account_key=$2
blob_container_name=$3

# Fetch data:
cp ../data/${product_info_file} .

# Unzip data:
mkdir product_info && mv ${product_info_file} product_info/
cd product_info && tar -xvzf ${product_info_file} && cd ..

# Upload data to storage account blob container:
echo "Uploading files to blob container..."
# Default: Uses Azure CLI login authentication.
# az storage blob upload-batch \
#     --auth-mode login \
#     --destination ${blob_container_name} \
#     --account-name ${storage_account_name} \
#     --source "product_info" \
#     --pattern "*.md" \
#     --overwrite
# If you want to use the old authentication method (account key), use "--auth-mode key" and provide the account key.
az storage blob upload-batch \
    --auth-mode key \
    --account-key ${storage_account_key} \
    --destination ${blob_container_name} \
    --account-name ${storage_account_name} \
    --source "product_info" \
    --pattern "*.md" \
    --overwrite

# Run setup:
echo "Running search setup..."
python3 search_setup.py

# Cleanup:
rm -rf product_info/
cd ${cwd}

echo "Search setup complete"
