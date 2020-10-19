import subprocess
import settings
from bemoss_lib.platform import bem_ctl
def agentstats():
    #returns a list of running agents and their status
    statusreply = bem_ctl.send_command('status')
    statusreply = statusreply.split('\n')[0:-1] #Ignore the last line
    result = {}
    for line in statusreply:
        #print(line, end='') #write to a next file name outfile
        words = line.split()
        if len(words) >= 3:
            result[words[1]] = words[2]
    return result

#print agentstats()