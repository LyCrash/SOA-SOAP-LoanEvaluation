import os
import subprocess
import time
import signal
import sys

# --- CONFIG --- #
SERVICES = [
    ("Information Extraction", "services/information_extraction.py", 8001),
    ("Credit Check", "services/credit_check.py", 8002),
    ("Property Evaluation", "services/property_evaluation.py", 8003),
    ("Decision Service", "services/decision_service.py", 8004),
    ("Composite Service", "composite_service/service_composite.py", 8000),
]

PYTHON = sys.executable  # automatically uses your venv Python interpreter
PROCESSES = []


def run_service(name, script, port):
    """Start one service as a subprocess."""
    print(f"🚀 Starting {name} on port {port}...")
    proc = subprocess.Popen([PYTHON, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    PROCESSES.append((name, proc))
    time.sleep(1)  # Give the service time to start
    if proc.poll() is None:
        print(f"✅ {name} running (PID: {proc.pid})")
    else:
        print(f"❌ Failed to start {name} — check logs below:")
        stdout, stderr = proc.communicate()
        print(stderr.decode())
    return proc


def start_all():
    """Launch all services sequentially."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)

    for name, script, port in SERVICES:
        script_path = os.path.join(base_path, script)
        if not os.path.exists(script_path):
            print(f"⚠️ Warning: script not found -> {script_path}")
            continue
        run_service(name, script_path, port)
        time.sleep(2)  # small delay between launches

    print("\n🌐 All services started successfully!\n")
    print("🧩 Composite service is available at:")
    print("   👉 http://127.0.0.1:8000/LoanEvaluationService?wsdl\n")


def stop_all():
    """Gracefully stop all running services."""
    print("\n🛑 Stopping all services...")
    for name, proc in PROCESSES:
        if proc.poll() is None:
            print(f"Terminating {name} (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}")
                proc.kill()
    print("✅ All services stopped.")


if __name__ == "__main__":
    try:
        start_all()
        print("🔄 Press Ctrl+C to stop all services.\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        stop_all()
