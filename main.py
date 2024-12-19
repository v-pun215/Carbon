import minecraft_launcher_lib as mclib
import sys, os, platform, psutil, json, getpass, requests, keys, subprocess, uuid
from threading import Thread
import keyboard,time

class Carbon():
    def runCarbon(self):
        '''          Variables        '''
        args = sys.argv
        name = args[0]
        os.system("title Carbon")
        os.system("cls")
        text = "Loading Argon..."
        self.log(text)
        svmem = psutil.virtual_memory()
        global usr_accnt
        usr_accnt = getpass.getuser()
        global currn_dir
        currn_dir = os.getcwd()
        global mc_dir
        if os.path.exists(r"C:\\Users\\{}\\AppData\\Roaming\\.minecraft".format(usr_accnt)):
            mc_dir = r"C:\\Users\\{}\\AppData\\Roaming\\.minecraft".format(usr_accnt)
        else:
            os.mkdir(r"C:\\Users\\{}\\AppData\\Roaming\\.minecraft".format(usr_accnt))
            mc_dir = r"C:\\Users\\{}\\AppData\\Roaming\\.minecraft".format(usr_accnt)
        java_home = str(os.environ.get('JAVA_HOME').replace("\\", "/")) + "/bin/java.exe"

        def get_size(bytes, suffix="B"):
            #Found this on some website, i don't remember now. Used to get the total ram in GB.
            """
            Scale bytes to its proper format
            e.g:
                1253656 => '1.20MB'
                1253656678 => '1.17GB'
            """
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor

        if not os.path.exists("settings.json"):
            settings = {
                        "accessToken": None,
                        "clientToken": None,
                        "refreshToken": None,
                        "User-info" : [
                            {
                                "username": None,
                                "AUTH_TYPE": None,
                                "UUID": None
                            }
                        ],
                        "PC-info" : [
                            {
                                "OS": platform.platform(),
                                "Total-Ram": f"{get_size(svmem.total)}",
                            }
                        ],
                        "Minecraft-home" : mc_dir,
                        "selected-version": "release" + " " + mclib.utils.get_latest_version()['release'],
                        "allocated_ram" : 3000,
                        "jvm-args": None,
                        "executablePath": java_home,
                        "firstLaunch": True
                    }
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
                f.close()
            
        else:
            pass

        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')  #Trailing commas in dict cause file read problems, these lines will fix it.
            s = s.replace('\n','')  #Found this on stackoverflow.
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)
            #print(json.dumps(data, indent=4,))

        '''          Settings        '''
        global os_name, mc_home, username, uid, accessToken, auth_type, jvm_args, selected_ver, allocated_ram, executablePath, firstLaunch, refreshToken
        os_name = data["PC-info"][0]["OS"]
        mc_home = data["Minecraft-home"]
        username = data["User-info"][0]["username"]
        uid = data["User-info"][0]["UUID"]
        accessToken = data["accessToken"]
        mc_dir = data["Minecraft-home"]
        auth_type = data["User-info"][0]["AUTH_TYPE"]
        jvm_args = data["jvm-args"]
        selected_ver = data["selected-version"]
        allocated_ram = data["allocated_ram"]
        executablePath = data["executablePath"]
        refreshToken = data["refreshToken"]
        firstLaunch = data["firstLaunch"]
        if firstLaunch == True:
            self.firstSetup()
        else:
            pass

        '''          Main        '''
        self.options = {
            "username": username,
            "uuid": uid,
            "token": accessToken,
            "executablePath": executablePath,
            "launcherName": "Carbon",
            "launcherVersion": "1.0",
        }
        if auth_type == "Microsoft":
            try:
                account_information = mclib.microsoft_account.complete_refresh(keys.clientId, keys.secret, keys.redirectURL, refreshToken)
                self.options = {
                    "username": account_information["name"],
                    "uuid": account_information["id"],
                    "token": account_information["access_token"],
                    "executablePath": executablePath,
                    "launcherName": "Carbon",
                    "launcherVersion": "1.0",
                }
            except mclib.exceptions.InvalidRefreshToken as e:
                print("Invalid Refresh Token, please relogin.")
                self.microsoftLogin()
                sys.exit()

        else:
            pass
        def main_ui():
            os.system("cls")
            
            welcome_str = "Welcome back, {}.".format(username)
            self.log(welcome_str)
            print(f"1. Play - {selected_ver}")
            print("2. Settings")
            print("3. Select Version")
            print("4. Exit")

            main_input = input()
            if main_input == "1":
                self.handle_run()
            elif main_input == "2":
                self.settings_ui()
                main_ui()
            elif main_input == "3":
                os.system("cls")
                version = input("Enter Version to select/download: ")
                for very in mclib.utils.get_version_list():
                    if very["id"] == version:
                        typee = very["type"]
                        break
                if self.check_version(version) == None:
                    print(version, "is not a valid version.")
                elif self.check_inst_version(version) == None:
                    print("Version not installed, Download?")
                    install = input("Y/N: ")
                    if install == "Y":
                        self.install_mc(str(typee + " "+version))
                    else:
                        main_ui()
                else:
                    with open("settings.json", "r") as js_read:
                        s = js_read.read()
                        s = s.replace('\t','')
                        s = s.replace('\n','')
                        s = s.replace(',}','}')
                        s = s.replace(',]',']')
                        data = json.loads(s)
                    data["selected-version"] = str(typee+" "+version)
                    with open("settings.json", "w") as f:
                        json.dump(data, f, indent=4 )
                        f.close()
                    print(f"Version '{str(typee).capitalize} {version}' selected.")
                self.pause()
                self.restartCarbon()
            elif main_input == "4":
                sys.exit(1)   
            else:
                main_ui()

        main_ui()
                    


    '''          Functions        '''
    def settings_ui(self):
        os.system("cls")
        self.log("Settings")
        print("1. Account Settings")
        print("2. Minecraft Settings")
        print("3. Back")
        settings_input = input()
        if settings_input == "1":
            os.system("cls")
            self.log("Account Settings")
            print("1. Change Account")
            print("2. Sign Out")
            print("3. Back")
            account_input = input()
            if account_input == "1":
                os.system("cls")
                self.log("Change Account")
                print("1. Microsoft")
                print("2. Offline")
                print("3. ElyBy")
                print("4. Back")
                change_input = input()
                if change_input == "1":
                    self.microsoftLogin()
                    self.restartCarbon()
                elif change_input == "2":
                    self.offlineLogin()
                    self.restartCarbon()
                elif change_input == "3":
                    self.elyByLogin()
                    self.restartCarbon()
                elif change_input == "4":
                    self.settings_ui()
                else:
                    print("Invalid Input.")
            elif account_input == "2":
                os.system("cls")
                self.log("Sign Out")
                print("Are you sure? This will delete all account data.")
                signout_input = input("Y/N: ")
                if signout_input == "Y" or signout_input == "y":
                    os.remove("settings.json")
                    print("Signed Out.")
                    os.system("pause")
                    self.restartCarbon()
                else:
                    pass
            elif account_input == "3":
                self.settings_ui()
            else:
                print("Invalid Input.")
        elif settings_input == "2":
            os.system("cls")
            self.log("Minecraft Settings")
            print("1. RAM")
            print("2. Downloaded Versions")
            print("3. JVM Arguments")
            print("4. Back")
            minecraft_input = input()
            if minecraft_input == "1":
                os.system("cls")
                self.log("RAM Settings")
                print("Current RAM: ", allocated_ram)
                ram_input = input("Enter RAM in MB: ")
                with open("settings.json", "r") as js_read:
                    s = js_read.read()
                    s = s.replace('\t','')
                    s = s.replace('\n','')
                    s = s.replace(',}','}')
                    s = s.replace(',]',']')
                    data = json.loads(s)
                data["allocated_ram"] = int(ram_input)
                with open("settings.json", "w") as f:
                    json.dump(data, f, indent=4 )
                    f.close()
                print("RAM Updated.")
                os.system("pause")
                self.settings_ui()
            elif minecraft_input == "2":
                os.system("cls")
                self.log("Downloaded Versions")
                print("1. List")
                print("2. Install")
                print("3. Uninstall")
                print("4. Back")
                download_input = input()
                if download_input == "1":
                    counter = 0
                    os.system("cls")
                    self.log("Downloaded Versions")
                    for version in mclib.utils.get_installed_versions(mc_dir):
                        counter += 1
                        print(str(counter)+".",version["id"])
                    os.system("pause")
                    self.settings_ui()
                elif download_input == "2":
                    self.log("Install")
                    self.install_mc(input("Enter Version: "))
                    os.system("pause")
                    self.settings_ui()
                elif download_input == "3":
                    self.log("Uninstall")
                    version = input("Enter Version: ")
                    if self.check_inst_version(version) == None:
                        print("Version not installed.")
                        os.system("pause")
                        self.settings_ui()
                    else:
                        os.chdir(mc_dir+"\\\\versions")
                        os.system(f"rmdir /s /q {version}")
                        os.system("pause")
                        self.settings_ui()
                elif download_input == "4":
                    self.settings_ui()
            elif minecraft_input == "3":
                os.system("cls")
                self.log("JVM Arguments")
                print("Current Arguments: ", jvm_args)
                jvm_input = input("Enter JVM Arguments: ")
                with open("settings.json", "r") as js_read:
                    s = js_read.read()
                    s = s.replace('\t','')
                    s = s.replace('\n','')
                    s = s.replace(',}','}')
                    s = s.replace(',]',']')
                    data = json.loads(s)
                data["jvm-args"] = jvm_input
                with open("settings.json", "w") as f:
                    json.dump(data, f, indent=4 )
                    f.close()
                print("JVM Arguments Updated.")
                os.system("pause")
                self.settings_ui()
            elif minecraft_input == "4":
                self.settings_ui()
            else:
                print("Invalid Input.")
        elif settings_input == "3":
            pass
                
                

                    

    def check_version(self, ver):
        for version in mclib.utils.get_version_list():
            if version["id"] == ver:
                return True
                break
    def restartCarbon(self):
        os.system("python main.py")
    def check_inst_version(self, ver):
        for version in mclib.utils.get_installed_versions(mc_dir):
            if version["id"] == ver:
                return True
                break
    def check_ver_type(ver):
        for version in mclib.utils.get_version_list():
            if version["id"] == ver:
                return version["type"]
                break
    def pause(self):
        print("Press Enter to continue...")
        while True:
            if keyboard.is_pressed('enter'):
                # Code to execute after Enter is pressed
                break
    def firstSetup(self):
        os.system("cls")
        print("Welcome to Carbon.")
        print("Select Login Method: ")
        print("1. Microsoft")
        print("2. Offline")
        print("3. ElyBy")
        loginnum = input("Enter Number: ")
        if loginnum == "1":
            self.microsoftLogin()
        elif loginnum == "2":
            self.offlineLogin()
        elif loginnum == "3":
            self.elyByLogin()
        else:
            print("Invalid Input.")
        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')
            s = s.replace('\n','')
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)

        data["firstLaunch"] = False

        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4 )
            f.close
        os.system("cls")
        self.restartCarbon()


    def microsoftLogin(self):
        subprocess.run(["python", "microsoftLogin.py"])

    def offlineLogin(self):
        print("Offline Login")
        username = input("Username: ")
        uid = uuid.uuid4()
        auth_type = "Offline"
        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')
            s = s.replace('\n','')
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)

        data["User-info"][0]["username"] = username
        data["User-info"][0]["UUID"] = str(uid)
        data["User-info"][0]["AUTH_TYPE"] = auth_type
        data["accessToken"] = ""
        data["clientToken"] = None
        data["refreshToken"] = None

        with open("settings.json", "w") as js_write:
            json.dump(data, js_write, indent=4)
            js_write.close()

    def elyByLogin(self):
        '''Connects to ely.by for user authorization'''
        username = input("Username: ")
        password = input("Password: ")

        self.usr = username
        self.pwd = password
        self.client_token = str(uuid.uuid4())

        self.acc_data ={
            "username": self.usr,
            "password": self.pwd,
            "clientToken" : self.client_token,
            "requestUser" : True
        }


        self.r = requests.get(f"https://authserver.ely.by/api/users/profiles/minecraft/{self.usr}")
        if self.r.status_code == 200:
            print("[OK] [200]", "User found, getting details........")
            self.r1 = requests.post(f"https://authserver.ely.by/auth/authenticate", data=self.acc_data)
            if self.r1.status_code == 200:
                self.accessToken = self.r1.json()["accessToken"]
                self.uid = self.r1.json()["user"]["id"]
                with open("settings.json", "r") as js_read:
                    s = js_read.read()
                    s = s.replace('\t','')
                    s = s.replace('\n','')
                    s = s.replace(',}','}')
                    s = s.replace(',]',']')
                    data = json.loads(s)

                data["User-info"][0]["UUID"] = self.uid
                data["clientToken"] = self.client_token
                data["accessToken"] = self.accessToken
                data["User-info"][0]["username"] = self.usr
                data["User-info"][0]["AUTH_TYPE"] = "ElyBy"

                with open("settings.json", "w") as f:
                    json.dump(data, f, indent=4 )
                    f.close()
            elif self.r1.status_code == 404:
                print("Data entered is either incomplete or account is secured with Oauth2")
        elif self.r.status_code == 404:
            print("[ERROR] 404", "User does not exist.")
    def log(self, text):
            columns, lines = os.get_terminal_size()
            width = columns
            print(text.center(width))

    def handle_run(self):
        os.system("cls")
        self.log("Minecraft Log")
        self.run_mc()
        self.restartCarbon()
        '''Creates the thread on which minecraft is running'''
        #self.t4 = Thread(target=self.run_mc)
        #self.t4.start()

        #self.monitor_mc(self.t4)

    def monitor_mc(self, t4):
        '''Monitors the thread on which minecraft is running'''
        if self.t4.is_alive():
            lambda: self.monitor_mc(self.t4)
        else:
            print("Minecraft Closed.")
            self.restartCarbon()
            t4.join(timeout=3.0)
            
    def run_mc(self):
        self.allocated_ram = allocated_ram
        self.modified_ram = self.allocated_ram//1
        self.ram_mb = int(self.modified_ram)

        self.ram_gb = self.allocated_ram//1000
        self.int_ram_gb = int(self.ram_gb)
        self.cpu_count = os.cpu_count()
        self.j1 = [f"-Xmx{int(self.ram_mb)}M", "-Xms128M"]
        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')
            s = s.replace('\n','')
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)
        data["jvm-args"] = self.j1
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4 )
            f.close()
        if auth_type == "Microsoft":
            if selected_ver.startswith("release"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
            elif selected_ver.startswith("snapshot"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
            else:
                print("Invalid Version")
        elif auth_type == "Offline":
            if selected_ver.startswith("release"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
            elif selected_ver.startswith("snapshot"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
            else:
                print("Invalid Version")

        elif auth_type == "ElyBy":
            self.j2 = [r"-javaagent:{}/authlib/".format(currn_dir) + "" + f"authlib-injector-1.2.5.jar=ely.by", f"-Xmx{int(self.ram_mb)}M", "-Xms128M"]
            if selected_ver.startswith("release"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
            elif selected_ver.startswith("snapshot"):
                self.options["jvmArguments"] = self.j1
                mc_ver = selected_ver.split(" ")[1]
                
                self.minecraft_command = mclib.command.get_minecraft_command(mc_ver, mc_dir, self.options)
                print(f"Launching minecraft version {selected_ver}")
                subprocess.call(self.minecraft_command)
    def printProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        self.percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        self.filledLength = int(length * iteration // total)
        self.bar = fill * self.filledLength + '-' * (length - self.filledLength)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'{self.percent}%', end=printEnd)
        
        # Print New Line on Complete
        if iteration == total:
            print()
    def maximum(self, max_value, value):
        self.max_value[0] = value
    def install_mc(self, version):
        for very in mclib.utils.get_version_list():
            if very["id"] == version:
                typee = very["type"]
                break
        self.selected_ver = str(typee)+ " "+version
        self.l5 = ""
        self.detected_ver1 = ""  # yet another small hack

        self.max_value = [0]

        self.callback = {
            "setStatus": lambda text: print(text),
            "setProgress": lambda value: self.printProgressBar(value, self.max_value[0]),
            "setMax": lambda value: self.maximum(self.max_value, value)
        }
        if self.selected_ver.startswith("release"):
                self.detected_ver1 = self.selected_ver.strip("release ")
        elif self.selected_ver.startswith("snapshot"):
                split_string = self.selected_ver.split(' ')
                new_string_list = split_string[1:]
                new_string = ' '.join(new_string_list)
                self.detected_ver1 = new_string
                print(self.detected_ver1)

        print(f"Installing {self.detected_ver1}")
        mclib.install.install_minecraft_version(self.detected_ver1,mc_dir, callback=self.callback)
        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')
            s = s.replace('\n','')
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)
        data["selected-version"] = self.selected_ver
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4)
            f.close()

        self.selected_version = data["selected-version"]
''' WIP '''
'''
class CMDLine:
    def __init__(self, carbon_instance):
        self.carbon = carbon_instance
        self.commands = {
            "launch": self.launch_minecraft,
            "set_ram": self.set_ram,
            "set_version": self.set_version,
            "help": self.show_help
        }
        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')
            s = s.replace('\n','')
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)

        data[""]
        self.run()

    def run(self):
        if len(sys.argv) < 2:
            self.show_help()
            return

        cmd = sys.argv[1]
        args = sys.argv[2:]

        if cmd in self.commands:
            self.commands[cmd](*args)
        else:
            print(f"Unknown command: {cmd}")
            self.show_help()

    def launch_minecraft(self, version=None):
        if version:
            self.set_version(version)
        self.carbon(Carbon()).handle_run()

    def set_ram(self, ram):
        try:
            ram = int(ram)
            with open("settings.json", "r") as js_read:
                data = json.load(js_read)
            data["allocated_ram"] = ram
            with open("settings.json", "w") as js_write:
                json.dump(data, js_write, indent=4)
            print(f"RAM set to {ram} MB")
        except ValueError:
            print("Invalid RAM value. Please enter an integer.")

    def set_version(self, version):
        for ver in mclib.utils.get_version_list():
            if ver["id"] == version:
                typee = ver["type"]
                break
        else:
            print(f"Version {version} not found.")
            return

        with open("settings.json", "r") as js_read:
            data = json.load(js_read)
        data["selected-version"] = f"{typee} {version}"
        with open("settings.json", "w") as js_write:
            json.dump(data, js_write, indent=4)
        print(f"Version set to {typee} {version}")

    def show_help(self):
        print("Available commands:")
        print("  launch [version] - Launch Minecraft with optional version")
        print("  set_ram <MB>     - Set allocated RAM in MB")
        print("  set_version <version> - Set Minecraft version")
        print("  help             - Show this help message")'''

if __name__ == "__main__":
    if len(sys.argv) > 1:
        '''WIP'''
        #carbon_instance = Carbon()
        #CMDLine(carbon_instance)
        pass
    else:
        Carbon.runCarbon(self=Carbon())