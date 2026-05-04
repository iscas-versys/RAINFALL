# RAINFALL — Installation Guide

This guide covers how to set up the required environment for RAINFALL.
---

## Dependencies

| Category               | Requirement                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------|
| **System**             | bash, cmake, make, gcc, git, wget, tar, xz-utils, libboost-all-dev                              |
| **LLVM toolchain**     | LLVM + Clang **12.0.1** – pre‑built archive provided by RAINFALL                                |
| **Custom tools**       | `veri-clang` & `veri-llvm-pass.so` – built from RAINFALL source                                 |
| **Python**             | Python 3.9+ (3.12 recommended) with `venv`                                                      |
| **Python packages**    | `requests`, `pycparser`, `clang==12.0.1` (Python bindings)                                     |
| **Ultimate Automizer** | Java 11+ (tested with OpenJDK 21), `wget`, `unzip`                                              |
| **Optional**           | `g++` – removes CDT “Cannot run program g++” warnings (not required for verification)           |
| **Environment**        | `PATH` must include `$ULTIMATE_DIR/adds`; `LLVM_COMPILER`, `VERI_LIB_PATH` (set by scripts)     |


---

## Quick Start
We also provide a complete artifact at https://drive.google.com/file/d/1Ct0qf3YeseJPNNpVB2N49KjRAnVXvD3L/view?usp=drive_link, which includes a full Docker environment and installation/usage steps. 

If you prefer not to use Docker, you can follow the steps below to install.


```bash


# 1. Clone the repository
git clone <repo-url> RAINFALL
cd RAINFALL

# 2. Install system build tools (cmake, boost, etc.)
#    Ubuntu / Debian:
apt update
apt install -y cmake libboost-all-dev xz-utils python3-venv
#    Fedora / CentOS: sudo dnf install cmake boost-devel

# 3. Create necessary directories that Git might not track
mkdir -p llvm/lib llvm/bin llvm/veri-clang/test/bin

# 4. Obtain LLVM 12.0.1 (if not already present)
bash ./scripts/requires/get_llvm.sh

# 5. Build veri-clang and the LLVM pass
bash ./scripts/install/install_veri-clang.sh

# 6. Create and activate a Python virtual environment
python3 -m venv rainfall_env
source rainfall_env/bin/activate

# 7. Install Python dependencies (exact clang version is important)
pip install --upgrade pip
pip install requests pycparser clang==12.0.1

# 8. Create required library symlink for libclang-12.so
cd clang+llvm/lib
ln -s libclang.so.12 libclang-12.so
cd ../..

# 9. Set the LLVM environment variables
source ./scripts/requires/init_env.sh

# 10. Configure your API keys (see Configuration section below)
cat > api_keys.json << 'EOF'
{
    "deepseek": {
        "api_key": "your-deepseek-api-key",
        "url": "https://api.deepseek.com/chat/completions"
    },
    "aliyun": {
        "api_key": "your-aliyun-api-key",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    },
    "openrouter": {
        "api_key": "your-openrouter-api-key",
        "url": "https://openrouter.ai/api/v1/chat/completions"
    }
}
EOF

# 11. INSTALL UAutomizer
apt-get update
apt-get install -y openjdk-21-jre wget unzip g++
cd Your_Project_Path
wget https://github.com/ultimate-pa/ultimate/releases/download/v0.3.1/UltimateAutomizer-linux.zip
unzip UltimateAutomizer-linux.zip
export PATH=/app/UAutomizer-linux/:$PATH

# 12. Run the termination analysis
python main.py     --llm-max 2 --iterate-max 5     --data-path="./data/eight_channel_data/eight_freqterm_process_data/data8/"     --result-path="./termination_result1"     --platform=deepseek     --model=deepseek-v4-pro    --ultimate-dir=/app/UAutomizer-linux
