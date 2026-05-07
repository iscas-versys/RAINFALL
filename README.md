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
## Resource Requirements

Based on actual measurement using `docker stats` during a full run:

| Resource        | Observed Peak    | Recommended (for safe execution)                |
|-----------------|------------------|-------------------------------------------------|
| **RAM**         | ~1 GB            | **≥ 2 GB**                                      |
| **CPU**         | ~670% (~6–7 cores) | **≥ 4 cores** (works with 1, but slower)        |
| **Network**     | minimal (only for LLM API calls) | stable internet connection when using cloud LLM |

*Run time: approximately 1 minute for the provided small example; full dataset evaluation may take several hours depending on LLM response time and iteration count.*

---

## Artifact Structure

```
RAINFALL/
├── README.md                       # This guide: setup, usage, expected output
├── LICENSE                         # Open-source license
├── main.py                         # Main entry point – runs termination analysis
├── utils.py                        # Utility functions (file I/O, logging, etc.)
├── prompt/                         # Prompt templates for the LLM (DeepSeek, etc.)
├── clang+llvm/                     # Pre-packaged Clang & LLVM 12.0.1 toolchain
├── data/                           # Benchmark / test datasets (C source files)
├── example/                        # Minimal working example for quick verification
│   ├── input/                      #   Input C program (e.g., a bounded loop)
│   │   └── for_bounded_loop1_*.c
│   └── output/                     #   Expected output files
│       ├── TerminalOutput.txt      #     Example of terminal output
│       └── termination_result_example/
│           ├── *.c                 #     Original source copy
│           ├── *_delLLMGen.c       #     Source with LLM-generated parts removed
│           ├── *.llm_log.txt       #     LLM interaction log
│           ├── *.graphml           #     Verification witness (GraphML)
│           ├── *.yml               #     Verification witness (YAML)
│           └── result_dict.txt     #     Final result summary
├── llvm/                           # LLVM IR-related scripts or intermediate files
├── scripts/                        # Install scripts and auxiliary tools
└── static_check/                   # Custom static checkers / analyser configurations
```
## Quick Start
We also provide a complete artifact at https://drive.google.com/file/d/1oToEX5eGJOnXxhceP2RoQGinkaAYbgaU/view?usp=drive_link (SHA256:9920791C30EFF15108DD8DC69F5FD24EB3C009824FEF4CE28967F2E892C1FA18), which includes a full Docker environment and installation/usage steps. 

## How to Run Using the Pre-built Docker Image

The artifact is shipped as a portable Docker image (`rainfall-artifact.tar`) that packs all required dependencies, tools, and test data. No additional installation is needed.

### Step 1: Load the Docker Image
```bash
docker load -i rainfall-artifact.tar
```
After loading, you should see the image `rainfall-artifact:v1` listed.
Verify with:
```bash
docker images | grep rainfall-artifact
```

### Step 2: Run a Container from the Image
```bash
docker run -it --name rainfall rainfall-artifact:v1
```
This will drop you into the container’s bash shell. All project files are located under `/artifact`.  
By default, the working directory is `/artifact/RAINFALL`.

> **Note**: If you need to run the container again after exiting, use `docker start -ai rainfall`.

### Step 3: Activate the Python Virtual Environment
Inside the container:
```bash
source /artifact/RAINFALL/rainfall_env/bin/activate
source ./scripts/requires/init_env.sh
```

### Step 4: Set Up the PATH for Ultimate Automizer
```bash
export PATH=/artifact/UAutomizer-linux/:$PATH
```

### Step 5: Provide Your LLM API Key
To use cloud‑based LLMs (DeepSeek, Aliyun, OpenRouter), you must create a file named `api_keys.json` in the working directory with your own API keys.  
**We do NOT include real keys in the artifact.**

Create the file (inside `/artifact/RAINFALL`):
```bash
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
```
Replace the placeholder text with your actual API keys. Only the services you intend to use need valid keys.

### Step 6: Run the Tool on the Provided Example
Execute the following command inside the container (still in `/artifact/RAINFALL`):
```bash
python main.py \
    --llm-max 2 \
    --iterate-max 5 \
    --data-path="./example/input/" \
    --result-path="./termination_result_example" \
    --platform=deepseek \
    --model=deepseek-v4-pro \
    --ultimate-dir=/artifact/UAutomizer-linux
```
This will run the termination analysis on the small example (a bounded loop program).

## How to Run without Docker

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
