# mcp_server/server.py
# SIFT-BENCH: Purpose-Built MCP Server
# Exposes SIFT forensic tools as safe, typed, read-only functions
# Agent CANNOT run destructive commands - architectural enforcement

import os
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

# Setup logging
os.makedirs("logs", exist_ok=True)
logger.add("logs/mcp_server.log", rotation="10 MB", level="DEBUG")

class SIFTMCPServer:
    """
    Purpose-built MCP Server for SIFT forensic tools.
    All functions are READ-ONLY by design.
    No destructive commands are exposed.
    """

    def __init__(self, evidence_path: str):
        self.evidence_path = Path(evidence_path)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.execution_log = []
        logger.info(f"MCP Server initialized | Session: {self.session_id}")
        logger.info(f"Evidence path: {self.evidence_path}")

    def _log_execution(self, tool_name: str, inputs: dict, output: dict):
        """Log every tool execution with timestamp for audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tool": tool_name,
            "inputs": inputs,
            "output_summary": str(output)[:500],
            "success": output.get("success", False)
        }
        self.execution_log.append(entry)
        logger.info(f"[TOOL EXECUTED] {tool_name} | Success: {entry['success']}")

    def _safe_read_file(self, filepath: str) -> Optional[str]:
        """Read a file safely - READ ONLY, never writes."""
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            if not path.is_file():
                return None
            with open(path, 'r', errors='replace') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return None

    def get_file_hash(self, filepath: str) -> dict:
        """
        Calculate MD5/SHA256 hash of a file.
        Used to verify evidence integrity.
        READ-ONLY operation.
        """
        tool_name = "get_file_hash"
        inputs = {"filepath": filepath}
        try:
            path = Path(filepath)
            if not path.exists():
                result = {"success": False, "error": f"File not found: {filepath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
                    sha256.update(chunk)

            result = {
                "success": True,
                "filepath": str(filepath),
                "md5": md5.hexdigest(),
                "sha256": sha256.hexdigest(),
                "size_bytes": path.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def list_directory(self, dirpath: str) -> dict:
        """
        List contents of a directory.
        READ-ONLY operation.
        """
        tool_name = "list_directory"
        inputs = {"dirpath": dirpath}
        try:
            path = Path(dirpath)
            if not path.exists():
                result = {"success": False, "error": f"Directory not found: {dirpath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            entries = []
            for item in path.iterdir():
                entries.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size_bytes": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })

            result = {
                "success": True,
                "dirpath": str(dirpath),
                "total_entries": len(entries),
                "entries": entries[:100]  # Limit to 100 entries
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def extract_strings(self, filepath: str, min_length: int = 4) -> dict:
        """
        Extract printable strings from a file.
        Simulates 'strings' command from SIFT.
        READ-ONLY operation.
        """
        tool_name = "extract_strings"
        inputs = {"filepath": filepath, "min_length": min_length}
        try:
            path = Path(filepath)
            if not path.exists():
                result = {"success": False, "error": f"File not found: {filepath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            with open(path, 'rb') as f:
                data = f.read()

            strings_found = []
            current = ""
            for byte in data:
                char = chr(byte)
                if char.isprintable() and char != '\n':
                    current += char
                else:
                    if len(current) >= min_length:
                        strings_found.append(current)
                    current = ""

            suspicious = [s for s in strings_found if any(
                keyword in s.lower() for keyword in
                ['cmd', 'powershell', 'http', 'download', 'execute',
                 'registry', 'system32', 'temp', 'malware', 'exploit']
            )]

            result = {
                "success": True,
                "filepath": str(filepath),
                "total_strings": len(strings_found),
                "suspicious_strings": suspicious[:50],
                "all_strings_sample": strings_found[:100]
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def analyze_file_metadata(self, filepath: str) -> dict:
        """
        Analyze file metadata - timestamps, permissions, size.
        Detects timestomping indicators.
        READ-ONLY operation.
        """
        tool_name = "analyze_file_metadata"
        inputs = {"filepath": filepath}
        try:
            path = Path(filepath)
            if not path.exists():
                result = {"success": False, "error": f"File not found: {filepath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            stat = path.stat()
            created = datetime.fromtimestamp(stat.st_ctime).isoformat()
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            accessed = datetime.fromtimestamp(stat.st_atime).isoformat()

            # Detect potential timestomping
            ctime = datetime.fromtimestamp(stat.st_ctime)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            time_diff = abs((ctime - mtime).total_seconds())
            timestomp_suspected = time_diff > 86400 * 30  # 30 days difference

            result = {
                "success": True,
                "filepath": str(filepath),
                "size_bytes": stat.st_size,
                "created": created,
                "modified": modified,
                "accessed": accessed,
                "timestomp_suspected": timestomp_suspected,
                "time_diff_seconds": time_diff,
                "extension": path.suffix,
                "is_hidden": path.name.startswith('.')
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def search_iocs(self, filepath: str) -> dict:
        """
        Search file for Indicators of Compromise (IOCs).
        Looks for IPs, URLs, registry keys, known malware patterns.
        READ-ONLY operation.
        """
        tool_name = "search_iocs"
        inputs = {"filepath": filepath}
        try:
            import re
            content = self._safe_read_file(filepath)
            if content is None:
                result = {"success": False, "error": f"Cannot read file: {filepath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            # Pattern matching for IOCs
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            registry_pattern = r'HKEY_[A-Z_]+\\[^\s]+'
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            ips = re.findall(ip_pattern, content)
            urls = re.findall(url_pattern, content)
            registry_keys = re.findall(registry_pattern, content)
            emails = re.findall(email_pattern, content)

            # Filter suspicious IPs (non-private)
            suspicious_ips = [ip for ip in ips if not (
                ip.startswith('192.168.') or
                ip.startswith('10.') or
                ip.startswith('127.') or
                ip.startswith('172.')
            )]

            result = {
                "success": True,
                "filepath": str(filepath),
                "suspicious_ips": list(set(suspicious_ips))[:20],
                "urls": list(set(urls))[:20],
                "registry_keys": list(set(registry_keys))[:20],
                "emails": list(set(emails))[:20],
                "total_iocs_found": len(suspicious_ips) + len(urls) + len(registry_keys)
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def check_persistence_mechanisms(self, dirpath: str) -> dict:
        """
        Check for common persistence mechanisms in a directory.
        Looks for startup entries, scheduled tasks, services.
        READ-ONLY operation.
        """
        tool_name = "check_persistence_mechanisms"
        inputs = {"dirpath": dirpath}
        try:
            path = Path(dirpath)
            if not path.exists():
                result = {"success": False, "error": f"Directory not found: {dirpath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            persistence_indicators = []
            suspicious_locations = [
                'startup', 'autorun', 'scheduled', 'cron',
                'init.d', 'systemd', 'launchd', 'registry'
            ]

            for item in path.rglob('*'):
                if item.is_file():
                    for indicator in suspicious_locations:
                        if indicator in str(item).lower():
                            persistence_indicators.append({
                                "file": str(item),
                                "indicator": indicator,
                                "size": item.stat().st_size,
                                "modified": datetime.fromtimestamp(
                                    item.stat().st_mtime).isoformat()
                            })

            result = {
                "success": True,
                "dirpath": str(dirpath),
                "persistence_indicators_found": len(persistence_indicators),
                "indicators": persistence_indicators[:20]
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def generate_timeline(self, dirpath: str) -> dict:
        """
        Generate a filesystem timeline from a directory.
        Sorts files by modification time.
        READ-ONLY operation.
        """
        tool_name = "generate_timeline"
        inputs = {"dirpath": dirpath}
        try:
            path = Path(dirpath)
            if not path.exists():
                result = {"success": False, "error": f"Directory not found: {dirpath}"}
                self._log_execution(tool_name, inputs, result)
                return result

            timeline = []
            for item in path.rglob('*'):
                if item.is_file():
                    stat = item.stat()
                    timeline.append({
                        "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "filepath": str(item),
                        "size_bytes": stat.st_size,
                        "action": "modified"
                    })

            # Sort by timestamp
            timeline.sort(key=lambda x: x['timestamp'])

            result = {
                "success": True,
                "dirpath": str(dirpath),
                "total_events": len(timeline),
                "timeline": timeline[:200],  # Limit output
                "earliest_event": timeline[0]['timestamp'] if timeline else None,
                "latest_event": timeline[-1]['timestamp'] if timeline else None
            }
            self._log_execution(tool_name, inputs, result)
            return result
        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log_execution(tool_name, inputs, result)
            return result

    def save_execution_log(self) -> str:
        """Save the full execution log to disk."""
        log_path = f"logs/execution_{self.session_id}.json"
        with open(log_path, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        logger.info(f"Execution log saved: {log_path}")
        return log_path

    def get_available_tools(self) -> list:
        """Return list of all available tools."""
        return [
            "get_file_hash",
            "list_directory",
            "extract_strings",
            "analyze_file_metadata",
            "search_iocs",
            "check_persistence_mechanisms",
            "generate_timeline"
        ]