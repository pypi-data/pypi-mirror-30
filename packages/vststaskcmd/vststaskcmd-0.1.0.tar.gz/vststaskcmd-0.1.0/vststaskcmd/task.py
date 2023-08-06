def setvariable(name, value, secret=False, silent=False):
    secretstring = ''
    logstring = ''
    if secret:
        secretstring = 'issecret=true;'
        logstring = ' as a secret'
    else:
        logstring = " to '{}'".format(value)
    print("##vso[task.setvariable variable={};{}]{}".format(name, secretstring, value))
    if not silent:
        print("VSTS variable '{}' is set{}".format(name,logstring))

def complete(result="Succeeded", comment=None):
    print("##vso[task.complete result={};]{}".format(result,comment))
    print("Current task result set to {}".format(result))

def setpartialsuccess(comment=None):
    complete("SucceededWithIssues", comment)

def setfailed(comment=None):
    complete("Failed", comment)