#!/bin/bash

# Script to generate gRPC Python code from proto files

echo "Generating gRPC code from proto files..."

# Determine Python binary (prefer project virtualenv if available)
if [ -d "venv" ] && [ -x "venv/bin/python" ]; then
    PYTHON_BIN="venv/bin/python"
else
    PYTHON_BIN=$(command -v python3 || command -v python)
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python interpreter not found" >&2
    exit 1
fi

# Generate Python code from proto files
"$PYTHON_BIN" -m grpc_tools.protoc \
    -I./app/grpc \
    --python_out=./app/grpc \
    --grpc_python_out=./app/grpc \
    --pyi_out=./app/grpc \
    ./app/grpc/catalogue.proto

# Fix imports to use package-relative form for generated gRPC stubs
if [ -f app/grpc/catalogue_pb2_grpc.py ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/^import catalogue_pb2/from . import catalogue_pb2/' app/grpc/catalogue_pb2_grpc.py
    else
        sed -i 's/^import catalogue_pb2/from . import catalogue_pb2/' app/grpc/catalogue_pb2_grpc.py
    fi
fi

# Ensure __init__.py exists
touch app/grpc/__init__.py

echo "gRPC code generation completed successfully!"
