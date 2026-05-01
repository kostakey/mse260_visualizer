#!/bin/bash
set -e

echo "=============================="
echo "  Setting up Python env"
echo "=============================="

# Create venv
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip

echo "Installing Python requirements..."
pip install -r requirements.txt


echo "=============================="
echo "  Building LAMMPS"
echo "=============================="

# Go to LAMMPS source
cd external/lammps

# clean build folder (safe rerun)
mkdir -p build
cd build

cmake ../cmake \
    -D PKG_PYTHON=ON \
    -D BUILD_SHARED_LIBS=ON

make -j$(nproc)

echo "Installing LAMMPS Python bindings..."
make install-python || true

cd ../../..

echo "=============================="
echo "  Environment ready"
echo "=============================="

echo "Activate with:"
echo "source .venv/bin/activate"