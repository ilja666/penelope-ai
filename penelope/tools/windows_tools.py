#!/usr/bin/env python3
"""
Windows System Automation Tools
Advanced Windows operations beyond basic app opening
"""
import os
import subprocess
import time
import platform
from typing import Dict, List, Any, Optional
from pathlib import Path


def _run_powershell_command(command: str, timeout: int = 30) -> str:
    """Execute PowerShell command and return output"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout or result.stderr or "Command executed"
    except Exception as e:
        return f"Error: {str(e)}"


def get_system_info() -> str:
    """Get comprehensive Windows system information"""
    commands = [
        "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer",
        "Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, MaxClockSpeed",
        "Get-WmiObject Win32_PhysicalMemory | Measure-Object Capacity -Sum | Select-Object @{Name='TotalGB'; Expression={$_.Sum / 1GB}}",
        "Get-PSDrive C | Select-Object Used, Free, @{Name='TotalGB'; Expression={$_.Used + $_.Free}}"
    ]

    results = []
    for cmd in commands:
        results.append(_run_powershell_command(cmd))

    return "\n".join(results)


def manage_services(action: str, service_name: str = None) -> str:
    """Manage Windows services"""
    if action == "list":
        return _run_powershell_command("Get-Service | Select-Object Name, Status, DisplayName | Format-Table -AutoSize")

    elif action == "start" and service_name:
        return _run_powershell_command(f"Start-Service -Name '{service_name}'")

    elif action == "stop" and service_name:
        return _run_powershell_command(f"Stop-Service -Name '{service_name}'")

    elif action == "restart" and service_name:
        return _run_powershell_command(f"Restart-Service -Name '{service_name}'")

    elif action == "status" and service_name:
        return _run_powershell_command(f"Get-Service -Name '{service_name}' | Select-Object Name, Status, DisplayName")

    return "Error: Invalid action or missing service name"


def manage_processes(action: str, process_name: str = None) -> str:
    """Manage Windows processes"""
    if action == "list":
        return _run_powershell_command("Get-Process | Select-Object Name, Id, CPU, WorkingSet | Sort-Object CPU -Descending | Format-Table -AutoSize")

    elif action == "kill" and process_name:
        return _run_powershell_command(f"Stop-Process -Name '{process_name}' -Force")

    elif action == "find" and process_name:
        return _run_powershell_command(f"Get-Process -Name '{process_name}' | Select-Object Name, Id, CPU, WorkingSet")

    return "Error: Invalid action or missing process name"


def network_tools(action: str) -> str:
    """Network diagnostic tools"""
    if action == "connections":
        return _run_powershell_command("Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State | Format-Table -AutoSize")

    elif action == "interfaces":
        return _run_powershell_command("Get-NetAdapter | Select-Object Name, Status, MacAddress, LinkSpeed | Format-Table -AutoSize")

    elif action == "ping":
        return _run_powershell_command("Test-Connection -ComputerName google.com -Count 4")

    elif action == "dns":
        return _run_powershell_command("Resolve-DnsName google.com")

    elif action == "wifi":
        return _run_powershell_command("netsh wlan show networks")

    return "Error: Invalid network action"


def file_system_tools(action: str, path: str = None) -> str:
    """Advanced file system operations"""
    if action == "disk_usage":
        return _run_powershell_command("Get-PSDrive | Where-Object {$_.Provider -eq 'FileSystem'} | Select-Object Name, Used, Free, @{Name='TotalGB'; Expression={($_.Used + $_.Free)/1GB}} | Format-Table -AutoSize")

    elif action == "large_files" and path:
        return _run_powershell_command(f"Get-ChildItem -Path '{path}' -Recurse -File | Sort-Object Length -Descending | Select-Object FullName, Length, LastWriteTime -First 10 | Format-Table -AutoSize")

    elif action == "cleanup_temp":
        return _run_powershell_command("Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Temp files cleaned'")

    elif action == "recent_files" and path:
        return _run_powershell_command(f"Get-ChildItem -Path '{path}' -Recurse | Where-Object {{$_.LastWriteTime -gt (Get-Date).AddDays(-7)}} | Select-Object FullName, LastWriteTime | Sort-Object LastWriteTime -Descending | Format-Table -AutoSize")

    return "Error: Invalid file system action"


def system_maintenance(action: str) -> str:
    """System maintenance operations"""
    if action == "check_disk":
        return _run_powershell_command("chkdsk C: /f /r /x")

    elif action == "defrag":
        return _run_powershell_command("Optimize-Volume -DriveLetter C -Defrag")

    elif action == "update":
        return _run_powershell_command("Get-WindowsUpdate | Install-WindowsUpdate -AcceptAll -IgnoreReboot")

    elif action == "cleanmgr":
        return _run_powershell_command("cleanmgr /sagerun:1")

    return "Error: Invalid maintenance action"


def power_management(action: str) -> str:
    """Power management operations"""
    if action == "status":
        return _run_powershell_command("Get-WmiObject -Class Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus")

    elif action == "hibernate":
        return _run_powershell_command("shutdown /h")

    elif action == "sleep":
        return _run_powershell_command("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif action == "shutdown":
        delay = input("Shutdown delay in seconds (default 30): ") or "30"
        return _run_powershell_command(f"shutdown /s /t {delay}")

    elif action == "restart":
        delay = input("Restart delay in seconds (default 30): ") or "30"
        return _run_powershell_command(f"shutdown /r /t {delay}")

    return "Error: Invalid power action"


def registry_tools(action: str, key_path: str = None, value_name: str = None) -> str:
    """Windows Registry operations (USE WITH CAUTION)"""
    if action == "read" and key_path and value_name:
        return _run_powershell_command(f"Get-ItemProperty -Path '{key_path}' -Name '{value_name}'")

    elif action == "list" and key_path:
        return _run_powershell_command(f"Get-ChildItem -Path '{key_path}'")

    # Note: Write operations are dangerous and disabled for safety
    return "Error: Registry operations require explicit parameters or are disabled for safety"


def event_viewer(action: str, log_name: str = "System") -> str:
    """Windows Event Viewer operations"""
    if action == "recent_errors":
        return _run_powershell_command(f"Get-EventLog -LogName {log_name} -EntryType Error -Newest 10 | Format-Table -AutoSize")

    elif action == "recent_warnings":
        return _run_powershell_command(f"Get-EventLog -LogName {log_name} -EntryType Warning -Newest 10 | Format-Table -AutoSize")

    elif action == "application_errors":
        return _run_powershell_command("Get-EventLog -LogName Application -EntryType Error -Newest 5 | Format-Table -AutoSize")

    return "Error: Invalid event viewer action"


# Main interface function for Penelope
def control_windows(action: str, **kwargs) -> str:
    """
    Advanced Windows system control.

    Available actions:
    - "system_info": Get comprehensive system information
    - "services": Manage Windows services (list/start/stop/restart/status)
    - "processes": Manage processes (list/kill/find)
    - "network": Network diagnostics (connections/interfaces/ping/dns/wifi)
    - "filesystem": File system tools (disk_usage/large_files/cleanup/recent)
    - "maintenance": System maintenance (check_disk/defrag/update/cleanup)
    - "power": Power management (status/hibernate/sleep/shutdown/restart)
    - "registry": Registry operations (READ ONLY for safety)
    - "events": Event viewer (recent_errors/warnings/application_errors)
    """
    if platform.system() != "Windows":
        return "Error: Windows tools only work on Windows systems"

    try:
        if action == "system_info":
            return get_system_info()

        elif action == "services":
            service_action = kwargs.get("service_action", "list")
            service_name = kwargs.get("service_name")
            return manage_services(service_action, service_name)

        elif action == "processes":
            process_action = kwargs.get("process_action", "list")
            process_name = kwargs.get("process_name")
            return manage_processes(process_action, process_name)

        elif action == "network":
            network_action = kwargs.get("network_action", "connections")
            return network_tools(network_action)

        elif action == "filesystem":
            fs_action = kwargs.get("fs_action", "disk_usage")
            fs_path = kwargs.get("path")
            return file_system_tools(fs_action, fs_path)

        elif action == "maintenance":
            maint_action = kwargs.get("maint_action", "check_disk")
            return system_maintenance(maint_action)

        elif action == "power":
            power_action = kwargs.get("power_action", "status")
            return power_management(power_action)

        elif action == "registry":
            reg_action = kwargs.get("reg_action", "list")
            reg_path = kwargs.get("key_path")
            reg_value = kwargs.get("value_name")
            return registry_tools(reg_action, reg_path, reg_value)

        elif action == "events":
            event_action = kwargs.get("event_action", "recent_errors")
            log_name = kwargs.get("log_name", "System")
            return event_viewer(event_action, log_name)

        else:
            available_actions = [
                "system_info", "services", "processes", "network",
                "filesystem", "maintenance", "power", "registry", "events"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing Windows action '{action}': {str(e)}"