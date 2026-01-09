import time
import json
import os
import logging

logger = logging.getLogger("ArkOS.Foundry")

class FoundryMachine:
    def __init__(self, name, machine_type, at_cost_per_hour):
        self.name = name
        self.machine_type = machine_type
        self.at_cost_per_hour = at_cost_per_hour
        self.status = "IDLE"
        self.active_job = None

class FoundryJob:
    def __init__(self, job_id, user, machine_name, at_budget, blueprint_id):
        self.job_id = job_id
        self.user = user
        self.machine_name = machine_name
        self.at_budget = at_budget
        self.blueprint_id = blueprint_id
        self.status = "PENDING"
        self.start_time = None
        self.progress = 0

class OSEFoundry:
    """
    The heart of physical production.
    Links digital AT balance to mechanical execution.
    """
    def __init__(self, ledger, storage_path="ledger/foundry_state.json"):
        self.ledger = ledger
        self.storage_path = storage_path
        self.machines = {}
        self.jobs = {}
        self._load_state()
        
        # Seed default machines if empty
        if not self.machines:
            self.add_machine(FoundryMachine("3D-PRINTER-001", "3D_PRINTER", 0.5))
            self.add_machine(FoundryMachine("CNC-LASER-001", "CNC_LASER", 1.2))
            self.add_machine(FoundryMachine("HEAVY-TRACTOR-001", "MOBILE_FARM_UNIT", 5.0))

    def add_machine(self, machine):
        self.machines[machine.name] = machine
        self._save_state()

    def start_job(self, user, machine_name, at_amount, blueprint_id, job_type="BUILD"):
        if machine_name not in self.machines:
            return {"status": "error", "message": "Machine not found"}
        
        machine = self.machines[machine_name]
        
        # 1. Verify user has the AT in the ledger
        balance = self.ledger.get_balance(user)
        if balance < at_amount:
            return {"status": "error", "message": f"Insufficient AT balance. Required: {at_amount}, Has: {balance}"}
        
        # 2. Lock the AT (Burning labor to create matter)
        job_id = f"JOB-{int(time.time())}"
        self.ledger.add_transaction(sender=user, recipient="SYSTEM_FOUNDRY", amount=at_amount, task=f"Foundry {job_type}: {blueprint_id}")
        
        # 3. Initialize the job
        job = FoundryJob(job_id, user, machine_name, at_amount, blueprint_id)
        job.status = "RUNNING"
        job.start_time = time.time()
        job.job_type = job_type
        self.jobs[job_id] = job
        machine.status = "BUSY"
        machine.active_job = job_id
        
        self._save_state()
        return {"status": "success", "job_id": job_id, "type": job_type}

    def start_recycling_job(self, user, machine_name, material_id):
        """Processes waste (e.g. vape batteries) into usable assets."""
        # Recycling often costs less AT but produces raw materials for future builds
        return self.start_job(user, machine_name, 0.2, f"RECYCLE-{material_id}", job_type="RECYCLE")

    def get_status(self):
        return {
            "machines": {name: vars(m) for name, m in self.machines.items()},
            "active_jobs": {jid: vars(j) for jid, j in self.jobs.items() if j.status == "RUNNING"}
        }

    def _save_state(self):
        # In a real system, this would be a database table
        try:
            state = {
                "machines": {name: vars(m) for name, m in self.machines.items()},
                "jobs": {jid: vars(j) for jid, j in self.jobs.items()}
            }
            with open(self.storage_path, 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save foundry state: {e}")

    def _load_state(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    state = json.load(f)
                    for name, m_data in state.get("machines", {}).items():
                        m = FoundryMachine(m_data['name'], m_data['machine_type'], m_data['at_cost_per_hour'])
                        m.status = m_data['status']
                        m.active_job = m_data['active_job']
                        self.machines[name] = m
                    for jid, j_data in state.get("jobs", {}).items():
                        j = FoundryJob(j_data['job_id'], j_data['user'], j_data['machine_name'], j_data['at_budget'], j_data['blueprint_id'])
                        j.status = j_data['status']
                        j.start_time = j_data['start_time']
                        j.progress = j_data['progress']
                        self.jobs[jid] = j
            except Exception as e:
                logger.error(f"Failed to load foundry state: {e}")
