import paramiko
import threading
import select
import socket
import logging

logger = logging.getLogger('uvicorn.error')

def ssh_handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception:
        chan.close()
        return
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if not data: break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if not data: break
            sock.send(data)
    chan.close()
    sock.close()

def start_reverse_tunnel(config):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh_cfg = config['ssh']
    try:
        client.connect(
            ssh_cfg['host'], 
            username=ssh_cfg['user'], 
            key_filename=ssh_cfg['key_path']
        )

        transport = client.get_transport()
        transport.request_port_forward("", int(ssh_cfg['remote_port']))
        
        logger.info(f"SSH Tunnel established: {ssh_cfg['host']}:{ssh_cfg['remote_port']} -> localhost:{ssh_cfg['local_port']}")

        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            thr = threading.Thread(
                target=ssh_handler, 
                args=(chan, 'localhost', int(ssh_cfg['local_port'])),
                daemon=True
            )
            thr.start()
    except Exception as e:
        logger.error(f"Failed to establish SSH tunnel: {e}")