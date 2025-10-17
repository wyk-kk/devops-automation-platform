"""
SSH交互式会话管理
支持WebSocket连接的实时SSH终端
"""
import paramiko
import threading
import time
from typing import Optional, Callable
import io


class SSHSession:
    """SSH交互式会话管理"""
    
    def __init__(self, host: str, port: int, username: str, 
                 password: Optional[str] = None, ssh_key: Optional[str] = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_key = ssh_key
        
        self.client: Optional[paramiko.SSHClient] = None
        self.shell: Optional[paramiko.Channel] = None
        self.is_connected = False
        self.read_thread: Optional[threading.Thread] = None
        self.output_callback: Optional[Callable] = None
    
    def connect(self) -> tuple[bool, Optional[str]]:
        """建立SSH连接并启动交互式shell"""
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
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
            
            # 创建交互式shell
            self.shell = self.client.invoke_shell(
                term='xterm-256color',
                width=80,
                height=24
            )
            
            # 设置shell为非阻塞模式
            self.shell.setblocking(0)
            
            self.is_connected = True
            
            # 启动输出读取线程
            self.start_output_thread()
            
            return True, None
            
        except paramiko.AuthenticationException:
            return False, "认证失败：用户名或密码错误"
        except paramiko.SSHException as e:
            return False, f"SSH连接失败: {str(e)}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def start_output_thread(self):
        """启动输出读取线程"""
        def read_output():
            while self.is_connected and self.shell:
                try:
                    if self.shell.recv_ready():
                        data = self.shell.recv(4096)
                        if data and self.output_callback:
                            self.output_callback(data.decode('utf-8', errors='ignore'))
                    else:
                        time.sleep(0.01)
                except Exception as e:
                    print(f"读取输出错误: {e}")
                    break
        
        self.read_thread = threading.Thread(target=read_output, daemon=True)
        self.read_thread.start()
    
    def send_input(self, data: str):
        """发送输入到SSH"""
        if self.shell and self.is_connected:
            try:
                self.shell.send(data)
            except Exception as e:
                print(f"发送输入错误: {e}")
    
    def resize(self, cols: int, rows: int):
        """调整终端大小"""
        if self.shell and self.is_connected:
            try:
                self.shell.resize_pty(width=cols, height=rows)
            except Exception as e:
                print(f"调整终端大小错误: {e}")
    
    def close(self):
        """关闭SSH连接"""
        self.is_connected = False
        
        if self.shell:
            try:
                self.shell.close()
            except:
                pass
            self.shell = None
        
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        
        # 等待读取线程结束
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1)

