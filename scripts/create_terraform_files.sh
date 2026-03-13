#!/bin/bash

# This script creates standard Terraform infrastructure files in the ./terraform/ directory.

TF_DIR="../terraform"
FILES=(
  main.tf
  variables.tf
  artifact_registry.tf
  storage.tf
  outputs.tf
  terraform.tfvars
  .gitignore
)

mkdir -p "$TF_DIR"

for file in "${FILES[@]}"; do
  touch "$TF_DIR/$file"
done

echo "Created files:"
for file in "${FILES[@]}"; do
  echo "$TF_DIR/$file"
done