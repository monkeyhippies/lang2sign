from subprocess import Popen, PIPE, CalledProcessError

def run_bash_cmd(cmd):

    p = Popen(['bash', '-c', cmd], stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, cmd, output, stderr=error)
