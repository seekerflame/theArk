
import time
import logging

logger = logging.getLogger("ArkOS.Fishery")

class Fishery:
    """
    The Fishery: Safety Interlock System.
    Monitors for digital surveillance (brute force) and physical tampering.
    """
    STATES = ["STABLE", "SHIELDED", "LOCKDOWN"]

    def __init__(self, hardware_bridge=None):
        self.bridge = hardware_bridge
        self.state = "STABLE"
        self.threat_level = 0  # 0 to 100
        self.failed_auth_count = 0
        self.last_auth_failure = 0
        self.tamper_detected = False
        
        # Configuration
        self.SHIELD_THRESHOLD = 10   # 10 auth failures
        self.LOCKDOWN_THRESHOLD = 50 # 50 auth failures or physical tamper
        
        logger.info("🛡️  Fishery Safety Interlock INITIALIZED")

    def report_auth_failure(self):
        """Called by the Router/Identity system on failed logins."""
        now = time.time()
        # Reset if it's been a long time (cooldown)
        if now - self.last_auth_failure > 3600:
            self.failed_auth_count = 1
        else:
            self.failed_auth_count += 1
        
        self.last_auth_failure = now
        self._evaluate_state()
        
        if self.state != "STABLE":
            logger.warning(f"⚠️  THREAT DETECTED: State shifted to {self.state} (Failures: {self.failed_auth_count})")

    def heartbeat(self):
        """Periodic check of hardware integrity."""
        if self.bridge:
            telemetry = self.bridge.read_telemetry()
            if telemetry.get('tamper_alarm'):
                if not self.tamper_detected:
                    logger.critical("🚨 PHYSICAL TAMPER DETECTED!")
                self.tamper_detected = telemetry.get('tamper_alarm')
        
        self._evaluate_state()

    def _evaluate_state(self):
        # 1. Physics First (Lockdown on tampering)
        if self.tamper_detected:
            self.state = "LOCKDOWN"
            return

        # 2. Digital Intensity
        if self.failed_auth_count >= self.LOCKDOWN_THRESHOLD:
            self.state = "LOCKDOWN"
        elif self.failed_auth_count >= self.SHIELD_THRESHOLD:
            self.state = "SHIELDED"
        else:
            self.state = "STABLE"

    def is_intercepted(self):
        """Helper to check if the node is under active surveillance."""
        return self.state != "STABLE"

    def get_status(self):
        return {
            "state": self.state,
            "threat_level": self.threat_level,
            "failed_attempts": self.failed_auth_count,
            "tamper_active": self.tamper_detected
        }
