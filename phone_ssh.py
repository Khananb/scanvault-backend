import paramiko
import sys
import os

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


class PhoneSSH:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect('192.168.0.192', port=8022, username='u0_a260', password='000000', timeout=10)

    def exec(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err

    def read_file(self, path):
        if path.startswith("~"):
            path = "/data/data/com.termux/files/home" + path[1:]
        sftp = self.ssh.open_sftp()
        with sftp.open(path, 'r') as f:
            content = f.read().decode()
        sftp.close()
        return content

    def write_file(self, path, content):
        if path.startswith("~"):
            path = "/data/data/com.termux/files/home" + path[1:]
        sftp = self.ssh.open_sftp()
        with sftp.open(path, 'w') as f:
            f.write(content)
        sftp.close()

    def list_dir(self, path="~"):
        return self.exec(f"ls -la {path}")

    def download(self, remote, local):
        if remote.startswith("~"):
            remote = "/data/data/com.termux/files/home" + remote[1:]
        sftp = self.ssh.open_sftp()
        sftp.get(remote, local)
        sftp.close()

    def upload(self, local, remote):
        if remote.startswith("~"):
            remote = "/data/data/com.termux/files/home" + remote[1:]
        sftp = self.ssh.open_sftp()
        sftp.put(local, remote)
        sftp.close()

    def close(self):
        self.ssh.close()


if __name__ == "__main__":
    phone = PhoneSSH()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python phone_ssh.py exec <command>")
        print("  python phone_ssh.py read <path>")
        print("  python phone_ssh.py write <path> <content>")
        print("  python phone_ssh.py list [path]")
        print("  python phone_ssh.py download <remote> <local>")
        print("  python phone_ssh.py upload <local> <remote>")
        sys.exit(1)

    action = sys.argv[1]

    if action == "exec" and len(sys.argv) >= 3:
        cmd = " ".join(sys.argv[2:])
        print(phone.exec(cmd))

    elif action == "read" and len(sys.argv) >= 3:
        print(phone.read_file(sys.argv[2]))

    elif action == "write" and len(sys.argv) >= 4:
        phone.write_file(sys.argv[2], sys.argv[3])
        print("OK")

    elif action == "list":
        path = sys.argv[2] if len(sys.argv) >= 3 else "~"
        print(phone.list_dir(path))

    elif action == "download" and len(sys.argv) >= 4:
        phone.download(sys.argv[2], sys.argv[3])
        print("Downloaded")

    elif action == "upload" and len(sys.argv) >= 4:
        phone.upload(sys.argv[2], sys.argv[3])
        print("Uploaded")

    else:
        print("Invalid command")

    phone.close()
