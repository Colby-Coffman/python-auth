def configRead():
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        quiet = config['Config']['quiet']
        quiet = quiet.lower() in ("true")
    except KeyError:
        quiet = False
    try:
        alg = config['Config']['alg']
        alg = str(quiet).lower()
    except KeyError:
        print("ERROR: Algorithm not defined. Reverting to SHA256")
        alg = 'sha256'
    try:
        saltSize = config['Salt']['saltSize']
        saltSize = int(saltSize)
    except KeyError:
        saltSize = 8
        print("ERROR: saltSize not defined or not integer. Reverting to 8")
    return quiet,alg,saltSize

def salter(pswd,saltsize):
    import string
    import secrets
    alphabet = string.ascii_letters + string.digits
    salt = ''.join(secrets.choice(alphabet) for i in range(saltsize))
    return pswd+salt,salt

def init_usrs(nUsr, saltSize):
    import hashlib
    usrlist=[]
    for index in range(nUsr):
        usrname=''
        pswd=''
        while usrname=='':
            usrname = input("Enter username: ")
        while pswd=='':
            pswd = input("Enter password: ")
        pswd,salt = salter(pswd,saltSize)
        pswd = hashlib.sha256(pswd.encode()).hexdigest()
        usrlist.append([])
        usrlist[index].append(usrname)
        usrlist[index].append(pswd)
        usrlist[index].append(salt)
    return usrlist

def load_users():
    usrlist=[]
    saveFile = open("usrlist", "r")
    temp = saveFile.read().split(",")
    for x in range(len(temp)//3):
        usrlist.append([])
        usrlist[x].append(temp[(3*x)])
        usrlist[x].append(temp[(3*x)+1])
        usrlist[x].append(temp[(3*x)+2])
    saveFile.close()
    return usrlist

def save_users(usrlist,overWrite):
    if overWrite==True:
        saveFile = open("usrlist", "w")
    else:
        saveFile = open("usrlist", "r")
        if saveFile.read()!='':
            saveFile = open("usrlist", "a")
            saveFile.write(',')
        else:
            saveFile = open("usrlist", "a")
    if len(usrlist)>0:
        for x in range(len(usrlist)):
            if (x+1)<len(usrlist):
                saveFile.write(str(usrlist[x][0])+","+str(usrlist[x][1])+","+str(usrlist[x][2])+',')
            else:
                saveFile.write(str(usrlist[x][0])+","+str(usrlist[x][1])+","+str(usrlist[x][2]))
    else:
        saveFile.write('')
    saveFile.close()
   
def usr_check(usrn,pswd,usrlist):
    import hashlib
    index=0
    Ufound=False
    Pfound=False
    while Ufound==False and index<len(usrlist):
        if usrlist[index][0]==usrn:
            Ufound=True
            pswd=hashlib.sha256(str(pswd+str(usrlist[index][2])).encode()).hexdigest()
            if usrlist[index][1]==pswd:
                Pfound=True
            break
        index=index+1
    return Ufound,Pfound

def login_status(Ufound,Pfound,quiet):
    if quiet==False:
        if Ufound==True and Pfound==True:
            print("Access authorized")
            return True
        elif Ufound==True:
            print("Incorrect password. Access denied")
            return False
        else:
            print("User does not exist. Access denied")
            return False
    else:
        if Ufound==True and Pfound==True:
            return True
        else:
            return False
            
def login_init(usrname,pswd,overWrite,quiet,saltSize):
    import os
    import sys
    loginSt=False
    if os.path.isfile("usrlist") == False and overWrite==False:
        print("Userfile does not exist! Execute with overWrite set to 'True'")
        sys.exit()
    elif overWrite==True:
        if input("Do you want to overwrite the existing user list[y/N]? ").upper()=='Y':
            newFile=True
        else:
            newFile=False
        while True:
            nUsr=input("Enter the number of users to initialize ('0' Clears the database): ")
            try:
                nUsr=int(nUsr)
                break
            except ValueError:
                pass
        if nUsr>0:
            usrlist=init_usrs(nUsr,saltSize)
            save_users(usrlist,newFile)
        elif nUsr==0 and overWrite==True:
            save_users([],True)
    else:
        usrlist = load_users()
        Ufound,Pfound=usr_check(usrname,pswd,usrlist)
        loginSt=login_status(Ufound,Pfound,quiet)
    return loginSt


def Auth_test(quiet):
    import os
    configRead()
    try:
        print("[Authentication Test]".center(os.get_terminal_size().columns))
    except OSError:
        print("[Authentication Test]")
    usr=input("Input username: ")
    pswd=input("Input password: ")
#    if input("Enable quiet mode? [y/N]").upper() == "Y":
#        quiet=True
#    else:
#        quiet=False
    loginSuccess=login_init(usr,pswd,False,quiet,0)
    if quiet!=True:
        print("Login success status:", loginSuccess)
    else:
        print(loginSuccess)

def main_menu():
    quiet,alg,saltSize=configRead()
    print("\n--- Main Menu ---")
    print("0. Initialize user accounts")
    print("1. Test Authentication")
    print("2. Exit")
    choice = input("Enter your choice: ")
    if choice == '0':
        login_init('','',True,quiet,saltSize)
    elif choice == '1':
        Auth_test(quiet)
    elif choice == '2':
        print("Exiting program.")
        exit()
    else:
        print("Invalid choice. Please enter 0, 1 or 2.")
        main_menu()

if __name__ == "__main__":
    while True:
        main_menu()
