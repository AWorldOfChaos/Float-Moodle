import subprocess
import sys
proc = subprocess.Popen(['python', sys.argv[1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
marks = 0
if proc.communicate()[0] == b'hello world\r\n':
    marks = 1

print(marks)

