import paramiko
from typing import Tuple, Optional
import io


class SSHClient:
    """SSH客户端封装"""
    
    def __init__(self, host: str, port: int, username: str, password: Optional[str] = None, 
                 ssh_key: Optional[str] = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_key = ssh_key
        self.client = None
    
    def connect(self) -> bool:
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.ssh_key:
                # 使用SSH密钥认证
                key_file = io.StringIO(self.ssh_key)
                pkey = paramiko.RSAKey.from_private_key(key_file)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=pkey,
                    timeout=10
                )
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10
                )
            return True
        except Exception as e:
            print(f"SSH connection failed: {str(e)}")
            return False
    
    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """执行命令
        
        Returns:
            (stdout, stderr, exit_code)
        """
        if not self.client:
            raise Exception("Not connected")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            
            return stdout_str, stderr_str, exit_code
        except Exception as e:
            return "", str(e), -1
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """上传文件"""
        if not self.client:
            raise Exception("Not connected")
        
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            print(f"File upload failed: {str(e)}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        if not self.client:
            raise Exception("Not connected")
        
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return True
        except Exception as e:
            print(f"File download failed: {str(e)}")
            return False
    
    def get_system_info(self) -> dict:
        """获取系统信息"""
        info = {}
        
        # 操作系统信息
        stdout, _, _ = self.execute_command("uname -s")
        info['os_type'] = stdout.strip()
        
        stdout, _, _ = self.execute_command("uname -r")
        info['os_version'] = stdout.strip()
        
        # CPU核心数
        stdout, _, _ = self.execute_command("nproc")
        try:
            info['cpu_cores'] = int(stdout.strip())
        except:
            info['cpu_cores'] = 0
        
        # 内存总量（MB）
        stdout, _, _ = self.execute_command("free -m | grep Mem | awk '{print $2}'")
        try:
            info['memory_total'] = int(stdout.strip())
        except:
            info['memory_total'] = 0
        
        # 磁盘总量（GB）
        stdout, _, _ = self.execute_command("df -BG / | tail -1 | awk '{print $2}' | sed 's/G//'")
        try:
            info['disk_total'] = int(stdout.strip())
        except:
            info['disk_total'] = 0
        
        return info
    
    def get_resource_usage(self) -> dict:
        """获取资源使用情况"""
        usage = {}
        
        # CPU使用率
        stdout, _, _ = self.execute_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
        try:
            usage['cpu_percent'] = float(stdout.strip())
        except:
            usage['cpu_percent'] = 0.0
        
        # 内存使用情况
        stdout, _, _ = self.execute_command("free -m | grep Mem | awk '{print $3,$2}'")
        try:
            parts = stdout.strip().split()
            usage['memory_used'] = int(parts[0])
            usage['memory_total'] = int(parts[1])
            usage['memory_percent'] = round(usage['memory_used'] / usage['memory_total'] * 100, 2)
        except:
            usage['memory_used'] = 0
            usage['memory_total'] = 0
            usage['memory_percent'] = 0.0
        
        # 磁盘使用情况
        stdout, _, _ = self.execute_command("df -BG / | tail -1 | awk '{print $3,$2}' | sed 's/G//g'")
        try:
            parts = stdout.strip().split()
            usage['disk_used'] = int(parts[0])
            usage['disk_total'] = int(parts[1])
            usage['disk_percent'] = round(usage['disk_used'] / usage['disk_total'] * 100, 2)
        except:
            usage['disk_used'] = 0
            usage['disk_total'] = 0
            usage['disk_percent'] = 0.0
        
        # 系统运行时间
        stdout, _, _ = self.execute_command("uptime -p")
        usage['uptime'] = stdout.strip()
        
        return usage
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            self.client = None

