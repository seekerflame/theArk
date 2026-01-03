#!/bin/bash
echo "--- DIAGNOSTIC REPORT ---" > status_report.txt
date >> status_report.txt
echo "Checking Python:" >> status_report.txt
which python3 >> status_report.txt
echo "Checking Processes:" >> status_report.txt
ps aux | grep village | grep -v grep >> status_report.txt
ps aux | grep server.py | grep -v grep >> status_report.txt
echo "Checking Port 3000:" >> status_report.txt
lsof -i :3000 >> status_report.txt
echo "--- END ---" >> status_report.txt
