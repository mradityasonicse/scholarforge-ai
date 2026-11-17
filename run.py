import os
import sys
import time
import webbrowser
import threading
import uvicorn

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  ScholarForge AI - University Project Report Generator")
    print("  Server launching at: http://127.0.0.1:8000")
    print("=" * 60)
    
    # Auto open browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
