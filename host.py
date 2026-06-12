import os
import sys
import time
import threading
import subprocess
import http.server
import socketserver

PORT = 8000

def start_server():
    global PORT
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
    
    # Error Handling 1: Ensure the 'public' directory exists
    if not os.path.isdir(web_dir):
        print(f"[-] CRITICAL ERROR: Directory '{web_dir}' does not exist.")
        print("[-] Please ensure the 'public' folder is created and contains your website files.")
        os._exit(1)

    # Error Handling 2: Handle permission errors when changing directories
    try:
        os.chdir(web_dir)
    except PermissionError:
        print(f"[-] CRITICAL ERROR: Permission denied when accessing '{web_dir}'.")
        os._exit(1)
    except Exception as e:
        print(f"[-] CRITICAL ERROR: Unexpected error changing directory: {e}")
        os._exit(1)
    class FilteredRequestHandler(http.server.SimpleHTTPRequestHandler):
        def is_allowed_user_agent(self):
            user_agent = self.headers.get('User-Agent', '').lower()
            # Block Mac and Mobile devices
            blocked_keywords = ['iphone', 'ipad', 'android', 'macintosh', 'mac os x', 'mobile']
            for keyword in blocked_keywords:
                if keyword in user_agent:
                    print(f"\n[!] Blocked access from device: {user_agent}")
                    return False
            return True

        def do_GET(self):
            if not self.is_allowed_user_agent():
                self.send_error(404, "Not Found")
                return
            super().do_GET()

        def do_HEAD(self):
            if not self.is_allowed_user_agent():
                self.send_error(404, "Not Found")
                return
            super().do_HEAD()

    Handler = FilteredRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    # Error Handling 3: Handle Port conflicts (e.g. port 8000 already in use)
    httpd = None
    max_retries = 5
    for attempt in range(max_retries):
        try:
            httpd = socketserver.TCPServer(("", PORT), Handler)
            break
        except OSError as e:
            # Check for standard "Address already in use" error numbers
            if e.errno == 98 or e.errno == 10048: 
                print(f"[*] Port {PORT} is in use. Trying port {PORT + 1}...")
                PORT += 1
            else:
                print(f"[-] Error binding to port {PORT}: {e}")
                os._exit(1)
    
    if not httpd:
        print(f"[-] CRITICAL ERROR: Could not find an available port after {max_retries} attempts.")
        os._exit(1)

    print(f"[*] Local HTTP server successfully running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except Exception as e:
        print(f"[-] Local server encountered an error: {e}")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    # Start the local HTTP server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("[*] Preparing local environment...")
    
    # Give the local server a brief moment to initialize and lock its port
    time.sleep(1.5)
    
    # Error Handling 4: Check if the server thread crashed during startup
    if not server_thread.is_alive():
        print("[-] Local server failed to start. Exiting script.")
        sys.exit(1)

    print(f"[*] Launching Cloudflare Quick Tunnel on port {PORT}...")
    
    # Check if cloudflared exists globally or locally
    cloudflared_path = "cloudflared"
    import shutil
    if not shutil.which(cloudflared_path) and not os.path.exists("cloudflared.exe"):
        print("\n[*] 'cloudflared' not found on your system!")
        if os.name == 'nt':
            print("[*] Automatically downloading cloudflared.exe for Windows...")
            import urllib.request
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            try:
                urllib.request.urlretrieve(url, "cloudflared.exe")
                print("[*] Download complete!")
                cloudflared_path = "cloudflared.exe"
            except Exception as e:
                print(f"[-] Failed to download cloudflared automatically: {e}")
                sys.exit(1)
        else:
            print("[-] Please install cloudflared manually for your OS.")
            sys.exit(1)
    elif os.path.exists("cloudflared.exe"):
        cloudflared_path = "cloudflared.exe"
    
    try:
        # Error Handling 5: Safely execute cloudflared and catch subprocess issues
        subprocess.run(
            [cloudflared_path, "tunnel", "--url", f"http://localhost:{PORT}"],
            check=True
        )
    except FileNotFoundError:
        print("\n[-] CRITICAL ERROR: 'cloudflared' executable could not be run.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Cloudflare Tunnel terminated unexpectedly with exit code: {e.returncode}")
        print("[-] This can happen if your internet connection drops or if Cloudflare rejects the connection.")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n[*]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] An unexpected system error occurred: {e}")
        sys.exit(1)
