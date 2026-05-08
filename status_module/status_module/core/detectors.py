"""
Detectors — low-level OS queries.
All functions are cross-platform where possible (Windows primary, Linux fallback).
"""
import os, re, subprocess, platform, shutil
from datetime import datetime

SYSTEM = platform.system()   # "Windows" | "Linux" | "Darwin"


# ── Process list ──────────────────────────────────────────────

def get_processes() -> list[dict]:
    """Return list of {pid, name, cpu, mem} for all running processes."""
    try:
        if SYSTEM == "Windows":
            out = subprocess.check_output(
                "tasklist /FO CSV /NH", shell=True, text=True, timeout=10
            )
            procs = []
            for line in out.strip().splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 5:
                    procs.append({
                        "name": parts[0].lower(),
                        "pid":  parts[1],
                        "mem":  parts[4],
                        "cpu":  "N/A"
                    })
            return procs
        else:
            out = subprocess.check_output(
                ["ps", "aux"], text=True, timeout=10
            )
            procs = []
            for line in out.strip().splitlines()[1:]:
                cols = line.split(None, 10)
                if len(cols) >= 11:
                    procs.append({
                        "name": cols[10].split("/")[-1].split()[0].lower(),
                        "pid":  cols[1],
                        "cpu":  cols[2],
                        "mem":  cols[3],
                    })
            return procs
    except Exception as e:
        return [{"error": str(e)}]


def is_process_running(name: str) -> dict:
    """Check if a process matching name is running."""
    name_lower = name.lower().replace(".exe", "")
    procs = get_processes()
    matches = [
        p for p in procs
        if name_lower in p.get("name", "").replace(".exe", "")
    ]
    return {
        "running":  bool(matches),
        "count":    len(matches),
        "matches":  matches[:5],   # cap at 5
        "query":    name,
    }


# ── Open windows (Windows only, stubbed on Linux) ────────────

def get_open_windows() -> list[str]:
    """Return list of visible window titles (Windows only)."""
    if SYSTEM != "Windows":
        return ["[open_windows not available on non-Windows]"]
    try:
        # Use PowerShell to enumerate window titles
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "[System.Windows.Forms.Application]::OpenForms | "
            "ForEach-Object {$_.Text}"
        )
        out = subprocess.check_output(
            ["powershell", "-Command", script],
            text=True, timeout=10, stderr=subprocess.DEVNULL
        )
        titles = [t.strip() for t in out.strip().splitlines() if t.strip()]
        if not titles:
            # Fallback: use tasklist with window titles via wmic
            out2 = subprocess.check_output(
                'wmic process where "not name=\'\'" get name,processid,description',
                shell=True, text=True, timeout=10
            )
            titles = list({
                line.split()[0] for line in out2.strip().splitlines()[1:]
                if line.strip()
            })
        return titles
    except Exception as e:
        return [f"Error: {e}"]


# ── File system ───────────────────────────────────────────────

def is_file_present(path: str) -> dict:
    """Check if a file or directory exists."""
    exists  = os.path.exists(path)
    is_file = os.path.isfile(path)
    is_dir  = os.path.isdir(path)
    size    = os.path.getsize(path) if is_file else None
    mtime   = None
    if exists:
        ts    = os.path.getmtime(path)
        mtime = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "exists":    exists,
        "is_file":   is_file,
        "is_dir":    is_dir,
        "size_bytes":size,
        "modified":  mtime,
        "path":      path,
    }


# ── System state ──────────────────────────────────────────────

def get_system_state() -> dict:
    """Snapshot of CPU, memory, disk, uptime, platform."""
    state = {
        "platform":    platform.system(),
        "os_version":  platform.version()[:80],
        "hostname":    platform.node(),
        "python":      platform.python_version(),
        "cpu_count":   os.cpu_count(),
        "timestamp":   datetime.now().isoformat(),
    }

    # CPU usage
    try:
        if SYSTEM == "Windows":
            out = subprocess.check_output(
                "wmic cpu get loadpercentage", shell=True, text=True, timeout=5
            )
            nums = re.findall(r"\d+", out)
            state["cpu_percent"] = int(nums[0]) if nums else "N/A"
        else:
            out = subprocess.check_output(
                "top -bn1 | grep 'Cpu(s)'", shell=True, text=True, timeout=5
            )
            m = re.search(r"(\d+\.\d+)\s*us", out)
            state["cpu_percent"] = float(m.group(1)) if m else "N/A"
    except Exception:
        state["cpu_percent"] = "N/A"

    # Memory
    try:
        if SYSTEM == "Windows":
            out = subprocess.check_output(
                "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value",
                shell=True, text=True, timeout=5
            )
            free  = int(re.search(r"FreePhysicalMemory=(\d+)", out).group(1))
            total = int(re.search(r"TotalVisibleMemorySize=(\d+)", out).group(1))
            state["ram_total_mb"] = round(total / 1024, 1)
            state["ram_free_mb"]  = round(free  / 1024, 1)
            state["ram_used_pct"] = round((1 - free / total) * 100, 1)
        else:
            out = subprocess.check_output(["free", "-m"], text=True, timeout=5)
            for line in out.splitlines():
                if line.startswith("Mem:"):
                    parts = line.split()
                    total = int(parts[1]); used = int(parts[2])
                    state["ram_total_mb"] = total
                    state["ram_free_mb"]  = total - used
                    state["ram_used_pct"] = round(used / total * 100, 1)
    except Exception:
        state["ram_total_mb"] = state["ram_free_mb"] = state["ram_used_pct"] = "N/A"

    # Disk (current drive)
    try:
        total, used, free = shutil.disk_usage("/")
        state["disk_total_gb"] = round(total / 1e9, 1)
        state["disk_free_gb"]  = round(free  / 1e9, 1)
        state["disk_used_pct"] = round(used  / total * 100, 1)
    except Exception:
        state["disk_total_gb"] = state["disk_free_gb"] = state["disk_used_pct"] = "N/A"

    return state


# ── Network (basic) ───────────────────────────────────────────

def get_network_state() -> dict:
    """Check internet connectivity and hostname."""
    import socket
    connected = False
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        connected = True
    except Exception:
        pass
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "Unknown"
    return {"internet": connected, "local_ip": ip}
