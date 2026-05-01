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

LAMMPS_DIR="external/lammps"

# Ensure external directory exists
mkdir -p external

# Clone LAMMPS if missing or broken
if [ ! -d "$LAMMPS_DIR/.git" ] || [ ! -d "$LAMMPS_DIR/cmake" ]; then
    echo "LAMMPS not found or incomplete. Cloning fresh copy..."

    rm -rf "$LAMMPS_DIR"
    git clone --depth 1 https://github.com/lammps/lammps.git "$LAMMPS_DIR"
fi

cd "$LAMMPS_DIR"

# Safety check (prevents silent failures)
if [ ! -d "cmake" ]; then
    echo "ERROR: LAMMPS clone failed or is corrupted"
    exit 1
fi

# Clean build (safe rerun)
rm -rf build
mkdir build
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
