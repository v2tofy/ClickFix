# ClickFix Educational Testing Framework

An educational framework designed to simulate, test, and analyze the "ClickFix" social engineering attack vector in a controlled environment. 

This project spins up a local Python server and automatically exposes it to the internet using a **Cloudflare Quick Tunnel** for easy testing without complex infrastructure setup. It is specifically built for cybersecurity education and awareness testing.

⚠️ **Disclaimer:** This tool is strictly for educational purposes and authorized penetration testing only. Do not use this framework for malicious activities.

## Features

- **ClickFix Simulation:** Includes an `index.html` payload template mimicking real-world social engineering tactics.
- **Device Filtering:** Built-in traffic filtering that blocks access from mobile devices (iOS/Android) and Mac computers, showing them a fake 404 error, to strictly target Windows PC environments.
- **Auto-Dependency Management:** If the Cloudflare Tunnel CLI (`cloudflared`) is missing on Windows, the script will automatically download and install it.
- **Port Conflict Auto-Resolution:** Automatically handles occupied ports by iterating until it finds an open one.
- **Instant Deployment:** Zero configuration required. Just run the batch file and share the generated `.trycloudflare.com` URL.

## Folder Structure

- `/public`: Place your educational payloads (e.g., `index.html`, CSS, images) inside this folder. The Python server explicitly serves files from this directory.
- `host.py`: The core Python engine that handles device filtering, local HTTP serving, auto-downloading dependencies, and executing the Cloudflare Tunnel.
- `run.bat`: A fast execution script for Windows. Double-click this to start the testing framework instantly.
- `requirements.txt`: Placeholder for future Python dependencies.

## Requirements

1. **Python 3.x** installed on your system.
2. *(Optional)* **Cloudflare Tunnel CLI (`cloudflared`)** - If not present, the script will download it automatically on Windows.

## How to Run

### Windows (Fast Method)
1. Double click `run.bat`.
2. Wait a moment while the script checks dependencies and starts the local server.
3. The script will generate a Cloudflare URL (e.g., `https://random-words.trycloudflare.com`). Use this URL for your testing.

### Command Line / Other OS
Run the host script directly from the terminal:
```bash
python host.py
```
