# SOP_Disk_Management: Ensuring Hardware Sovereignty

> [!IMPORTANT]
> **Issue**: External SSDs (especially ExFAT formatted ones) are prone to disconnection and "file system dirty" states if disconnected without unmounting.

## 1. Preventive Measures

### A. The "Golden Rule" of Unmounting

- **NEVER** unplug the SSD without ejecting it first in macOS.
- If the drive is in use by a process (e.g., Python server, terminal open in `/Volumes/Extreme SSD`), it will fail to eject and become "dirty."

### B. Hardware Integrity

- Avoid USB hubs. Plug the SanDisk Extreme directly into the Mac's Thunderbolt/USB-C ports.
- Hubs often experience power fluctuations that cause "silent" disconnections during high-load write operations.

### C. Recommended Filesystem (Future)

- **APFS (Apple File System)** is significantly more resilient for macOS-only work.
- **Tactical Strategy**: If cross-platform use is vital, maintain the master drive as ExFAT but consider a local **APFS Partition** or an APFS sparse disk image for "Private/Active" work during high-intensity sessions to prevent I/O hangs.

## 2. Recovery Protocol (If Drive is Greyed Out)

If the drive appears in Disk Utility but is greyed out (unmounted):

1. **Terminal Refresh**:

   ```bash
   ls -la /Volumes
   ```

   *Sometimes the directory exists but is empty. Delete the ghost directory if needed (requires sudo).*

2. **Force Mount**:
   Open Terminal and run:

   ```bash
   diskutil mount "/Volumes/Extreme SSD"
   ```

3. **Repair Volume**:
   If mounting fails:

   ```bash
   diskutil verifyVolume "/Volumes/Extreme SSD"
   diskutil repairVolume "/Volumes/Extreme SSD"
   ```

4. **Kill Diskarbitration**:
   If Disk Utility hangs:

   ```bash
   sudo killall diskarbitrationd
   ```

## 3. Incident Logging

- Every unexpected disconnection must be logged in `CHRONICLE/FAILURE_LOG.md` to track hardware degradation.
