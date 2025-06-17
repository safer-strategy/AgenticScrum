#!/usr/bin/env python3
"""MCP Service Management Utility for AgenticScrum."""

import argparse
import subprocess
import json
import time
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import sys
import os


class MCPServiceManager:
    """Manage MCP services lifecycle."""
    
    def __init__(self, project_root: str = "."):
        """Initialize MCP service manager."""
        self.project_root = Path(project_root).resolve()
        self.config_file = self.project_root / ".mcp.json"
        self.pid_dir = self.project_root / ".mcp_pids"
        self.log_dir = self.project_root / "logs"
        
        # Create directories if needed
        self.pid_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.log_dir / "mcp_manager.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"MCP configuration not found at {self.config_file}")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in MCP configuration: {e}")
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific MCP service."""
        try:
            config = self._load_config()
            
            if service_name not in config.get("mcpServers", {}):
                self.logger.error(f"Service {service_name} not found in configuration")
                return False
            
            # Check if already running
            if self._is_service_running(service_name):
                self.logger.info(f"Service {service_name} is already running")
                return True
            
            service_config = config["mcpServers"][service_name]
            cmd = [service_config["command"]] + service_config["args"]
            
            # Prepare environment
            env = os.environ.copy()
            if "env" in service_config:
                env.update(service_config["env"])
            
            # Setup log files
            stdout_log = self.log_dir / f"{service_name}_stdout.log"
            stderr_log = self.log_dir / f"{service_name}_stderr.log"
            
            # Start the process
            self.logger.info(f"Starting {service_name} with command: {' '.join(cmd)}")
            
            with open(stdout_log, 'a') as stdout_file, open(stderr_log, 'a') as stderr_file:
                process = subprocess.Popen(
                    cmd,
                    cwd=self.project_root,
                    env=env,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            # Save PID
            pid_file = self.pid_dir / f"{service_name}.pid"
            pid_file.write_text(str(process.pid))
            
            # Wait a moment to check if process started successfully
            time.sleep(1)
            if process.poll() is None:
                self.logger.info(f"Started {service_name} (PID: {process.pid})")
                return True
            else:
                self.logger.error(f"Failed to start {service_name} - process exited immediately")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific MCP service."""
        try:
            pid_file = self.pid_dir / f"{service_name}.pid"
            
            if not pid_file.exists():
                self.logger.info(f"Service {service_name} is not running (no PID file)")
                return True
            
            pid = int(pid_file.read_text().strip())
            
            # Check if process is still running
            if not self._is_process_running(pid):
                self.logger.info(f"Service {service_name} was already stopped")
                pid_file.unlink()
                return True
            
            # Try graceful shutdown first
            self.logger.info(f"Stopping {service_name} (PID: {pid})")
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)  # Kill entire process group
                
                # Wait for graceful shutdown
                for i in range(10):  # Wait up to 10 seconds
                    if not self._is_process_running(pid):
                        break
                    time.sleep(1)
                
                # Force kill if still running
                if self._is_process_running(pid):
                    self.logger.warning(f"Force killing {service_name} (PID: {pid})")
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    time.sleep(1)
                
            except ProcessLookupError:
                # Process already dead
                pass
            
            # Clean up PID file
            pid_file.unlink()
            self.logger.info(f"Stopped {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific MCP service."""
        self.logger.info(f"Restarting {service_name}")
        success = self.stop_service(service_name)
        if success:
            time.sleep(2)  # Give it a moment
            success = self.start_service(service_name)
        return success
    
    def status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP services."""
        try:
            config = self._load_config()
            status = {}
            
            for service_name in config.get("mcpServers", {}):
                service_status = self._get_service_status(service_name)
                status[service_name] = service_status
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}
    
    def _get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific service."""
        pid_file = self.pid_dir / f"{service_name}.pid"
        
        if not pid_file.exists():
            return {
                "running": False,
                "pid": None,
                "uptime": None,
                "memory_usage": None
            }
        
        try:
            pid = int(pid_file.read_text().strip())
            
            if not self._is_process_running(pid):
                # Stale PID file
                pid_file.unlink()
                return {
                    "running": False,
                    "pid": None,
                    "uptime": None,
                    "memory_usage": None,
                    "error": "Stale PID file removed"
                }
            
            # Get process info if psutil is available
            try:
                import psutil
                process = psutil.Process(pid)
                memory_info = process.memory_info()
                create_time = process.create_time()
                uptime = time.time() - create_time
                
                return {
                    "running": True,
                    "pid": pid,
                    "uptime": uptime,
                    "memory_usage": memory_info.rss,  # Resident set size
                    "cpu_percent": process.cpu_percent(),
                    "command": ' '.join(process.cmdline())
                }
            except ImportError:
                # psutil not available, basic info only
                return {
                    "running": True,
                    "pid": pid,
                    "uptime": None,
                    "memory_usage": None
                }
                
        except Exception as e:
            return {
                "running": False,
                "pid": None,
                "uptime": None,
                "memory_usage": None,
                "error": str(e)
            }
    
    def _is_service_running(self, service_name: str) -> bool:
        """Check if a service is currently running."""
        pid_file = self.pid_dir / f"{service_name}.pid"
        
        if not pid_file.exists():
            return False
        
        try:
            pid = int(pid_file.read_text().strip())
            return self._is_process_running(pid)
        except (ValueError, OSError):
            return False
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            os.kill(pid, 0)  # Send signal 0 to check if process exists
            return True
        except OSError:
            return False
    
    def health_check(self, service_name: str) -> Dict[str, Any]:
        """Perform health check on service."""
        status = self._get_service_status(service_name)
        
        if not status["running"]:
            return {
                "healthy": False,
                "status": "stopped",
                "message": "Service is not running"
            }
        
        # Basic health check - if it's running, it's probably healthy
        # Could be extended to ping the service or check specific endpoints
        health_info = {
            "healthy": True,
            "status": "running",
            "pid": status["pid"],
            "uptime": status.get("uptime"),
            "memory_usage": status.get("memory_usage")
        }
        
        # Check memory usage if available
        if status.get("memory_usage"):
            memory_mb = status["memory_usage"] / (1024 * 1024)
            if memory_mb > 1000:  # > 1GB
                health_info["warnings"] = [f"High memory usage: {memory_mb:.1f}MB"]
        
        return health_info
    
    def start_all(self) -> Dict[str, bool]:
        """Start all configured MCP services."""
        try:
            config = self._load_config()
            results = {}
            
            for service_name in config.get("mcpServers", {}):
                results[service_name] = self.start_service(service_name)
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to start all services: {e}")
            return {"error": str(e)}
    
    def stop_all(self) -> Dict[str, bool]:
        """Stop all MCP services."""
        results = {}
        
        # Get all services from PID files
        if self.pid_dir.exists():
            for pid_file in self.pid_dir.glob("*.pid"):
                service_name = pid_file.stem
                results[service_name] = self.stop_service(service_name)
        
        return results
    
    def logs(self, service_name: str, lines: int = 50, follow: bool = False) -> None:
        """Show logs for a specific service."""
        stdout_log = self.log_dir / f"{service_name}_stdout.log"
        stderr_log = self.log_dir / f"{service_name}_stderr.log"
        
        if not stdout_log.exists() and not stderr_log.exists():
            print(f"No logs found for service {service_name}")
            return
        
        if follow:
            # Follow logs in real-time
            try:
                if stdout_log.exists():
                    subprocess.run(["tail", "-f", str(stdout_log)])
                else:
                    subprocess.run(["tail", "-f", str(stderr_log)])
            except KeyboardInterrupt:
                pass
        else:
            # Show last N lines
            if stdout_log.exists():
                print(f"=== STDOUT ({service_name}) ===")
                subprocess.run(["tail", "-n", str(lines), str(stdout_log)])
            
            if stderr_log.exists():
                print(f"=== STDERR ({service_name}) ===")
                subprocess.run(["tail", "-n", str(lines), str(stderr_log)])


def format_status_output(status: Dict[str, Dict[str, Any]]) -> None:
    """Format and print service status in a nice table."""
    if "error" in status:
        print(f"Error getting status: {status['error']}")
        return
    
    if not status:
        print("No MCP services configured")
        return
    
    print(f"{'Service':<15} {'Status':<10} {'PID':<8} {'Uptime':<15} {'Memory':<10}")
    print("-" * 70)
    
    for service_name, info in status.items():
        if info["running"]:
            uptime_str = ""
            if info.get("uptime"):
                uptime_sec = int(info["uptime"])
                hours = uptime_sec // 3600
                minutes = (uptime_sec % 3600) // 60
                uptime_str = f"{hours:02d}:{minutes:02d}"
            
            memory_str = ""
            if info.get("memory_usage"):
                memory_mb = info["memory_usage"] / (1024 * 1024)
                memory_str = f"{memory_mb:.1f}MB"
            
            print(f"{service_name:<15} {'✅ Running':<10} {info['pid']:<8} {uptime_str:<15} {memory_str:<10}")
        else:
            error_msg = info.get("error", "Stopped")
            print(f"{service_name:<15} {'❌ ' + error_msg:<10} {'-':<8} {'-':<15} {'-':<10}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="MCP Service Management Utility for AgenticScrum",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start datetime              # Start DateTime service
  %(prog)s stop --all                  # Stop all services
  %(prog)s status                      # Show status of all services
  %(prog)s restart datetime            # Restart DateTime service
  %(prog)s health datetime             # Check health of DateTime service
  %(prog)s logs datetime --follow      # Follow DateTime service logs
        """
    )
    
    parser.add_argument(
        "--project-root", "-p",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start MCP service(s)")
    start_parser.add_argument("service", nargs="?", help="Service name to start")
    start_parser.add_argument("--all", action="store_true", help="Start all services")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop MCP service(s)")
    stop_parser.add_argument("service", nargs="?", help="Service name to stop")
    stop_parser.add_argument("--all", action="store_true", help="Stop all services")
    
    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart MCP service")
    restart_parser.add_argument("service", help="Service name to restart")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument("service", help="Service name to check")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show service logs")
    logs_parser.add_argument("service", help="Service name")
    logs_parser.add_argument("--lines", "-n", type=int, default=50, help="Number of lines to show")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow logs")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MCPServiceManager(args.project_root)
    
    try:
        if args.command == "start":
            if args.all:
                results = manager.start_all()
                for service, success in results.items():
                    status = "✅ Started" if success else "❌ Failed"
                    print(f"{service}: {status}")
            elif args.service:
                success = manager.start_service(args.service)
                status = "✅ Started" if success else "❌ Failed"
                print(f"{args.service}: {status}")
            else:
                print("Error: Specify service name or use --all")
                
        elif args.command == "stop":
            if args.all:
                results = manager.stop_all()
                for service, success in results.items():
                    status = "✅ Stopped" if success else "❌ Failed"
                    print(f"{service}: {status}")
            elif args.service:
                success = manager.stop_service(args.service)
                status = "✅ Stopped" if success else "❌ Failed"
                print(f"{args.service}: {status}")
            else:
                print("Error: Specify service name or use --all")
                
        elif args.command == "restart":
            success = manager.restart_service(args.service)
            status = "✅ Restarted" if success else "❌ Failed"
            print(f"{args.service}: {status}")
            
        elif args.command == "status":
            status = manager.status()
            format_status_output(status)
            
        elif args.command == "health":
            health = manager.health_check(args.service)
            if health["healthy"]:
                print(f"✅ {args.service} is healthy")
                if health.get("warnings"):
                    for warning in health["warnings"]:
                        print(f"⚠️  Warning: {warning}")
            else:
                print(f"❌ {args.service} is unhealthy: {health['message']}")
            
            # Show details
            for key, value in health.items():
                if key not in ["healthy", "status", "message", "warnings"]:
                    print(f"  {key}: {value}")
                    
        elif args.command == "logs":
            manager.logs(args.service, args.lines, args.follow)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()