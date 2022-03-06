from subprocess import Popen, PIPE, STDOUT

def shell_output(cmd):
    ''' execute a shell command and get its output (stdout/stderr) '''
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    return p.communicate()[0]


def shell_rc_and_output(cmd):
    ''' execute a shell command and get its return code and output (stdout/stderr) '''
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    out = p.communicate()[0]
    rc = p.returncode
    return rc, out


if __name__ == "__main__":
    cmd = 'ls -l'
    print(shell_output(cmd))
    rc, out = shell_rc_and_output(cmd)
    print(rc)
    print('rc: {}, out: {}'.format(rc, out))
