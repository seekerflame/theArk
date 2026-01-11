import subprocess
import os
import time
import json
from core.config import BASE_DIR, LOGS_DIR

class AgentController:
    def __init__(self):
        self.services = {
            "server": {"cmd": ["python3", "server.py"], "pid_file": BASE_DIR / "server.pid"},
            "gaia_daemon": {"cmd": ["python3", "gaia_daemon.py"], "pid": None},
            "ai_orchestrator": {"cmd": ["python3", "ai_orchestrator.py"], "pid": None},
            "steward": {"cmd": ["python3", "ark_steward.py"], "pid": None},
            "mesh_bridge": {"cmd": ["python3", "federation/mesh_bridge.py"], "pid": None}
        }
        self.status_file = LOGS_DIR / "agent_status.json"

    def is_running(self, service_name):
        service = self.services.get(service_name)
        if not service: return False
        
        # Check PID file for server
        if "pid_file" in service:
            if service["pid_file"].exists():
                try:
                    pid = int(service["pid_file"].read_text().strip())
                    os.kill(pid, 0)
                    return True
                except (ProcessLookupError, ValueError):
                    pass
        
        # Check internal PID
        if service.get("pid"):
            try:
                os.kill(service["pid"], 0)
                return True
            except ProcessLookupError:
                service["pid"] = None
        
        return False

    def start_service(self, service_name):
        if self.is_running(service_name):
            return True
            
        service = self.services.get(service_name)
        log_file = LOGS_DIR / f"{service_name}.log"
        
        print(f"🚀 Starting {service_name}...")
        with open(log_file, "a") as f:
            proc = subprocess.Popen(
                service["cmd"],
                cwd=BASE_DIR,
                stdout=f,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setpgrp
            )
            service["pid"] = proc.pid
            
        return True

    def stop_service(self, service_name):
        service = self.services.get(service_name)
        if not service: return False
        
        if "pid_file" in service and service["pid_file"].exists():
            pid = int(service["pid_file"].read_text().strip())
            os.kill(pid, 15)
            service["pid_file"].unlink()
            return True
            
        if service.get("pid"):
            os.kill(service["pid"], 15)
            service["pid"] = None
            return True
            
        return False

    def update_status_report(self):
        report = {name: "RUNNING" if self.is_running(name) else "STOPPED" for name in self.services}
        with open(self.status_file, "w") as f:
            json.dump(report, f, indent=2)
        return report

if __name__ == "__main__":
    controller = AgentController()
    print(controller.update_status_report())
