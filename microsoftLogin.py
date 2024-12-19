from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, QLocale
import minecraft_launcher_lib
import json
import sys
import os, keys

CLIENT_ID = keys.clientId
REDIRECT_URL = keys.redirectURL
se = keys.secret

class LoginWindow(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login to Microsoft Account")

        # Set the path where the refresh token is saved
        self.refresh_token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_token.json")

        # Open the login url
        login_url, self.state, self.code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URL)
        self.load(QUrl(login_url))

        # Connects a function that is called when the url changed
        self.urlChanged.connect(self.new_url)

        self.show()

    def new_url(self, url: QUrl):
        try:
            # Get the code from the url
            auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(url.toString(), self.state)
            # Do the login
            account_information = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, se, REDIRECT_URL, auth_code, self.code_verifier)
            # Show the login information
            self.show_account_information(account_information)
        except AssertionError:
            print("States do not match!")
        except KeyError:
            print("Url not valid")

    def show_account_information(self, information_dict):
        information_string = f'Username: {information_dict["name"]}<br>'
        information_string += f'UUID: {information_dict["id"]}<br>'
        information_string += f'Token: {information_dict["access_token"]}<br>'

        with open("settings.json", "r") as js_read:
            s = js_read.read()
            s = s.replace('\t','')  #Trailing commas in dict cause file read problems, these lines will fix it.
            s = s.replace('\n','')  #Found this on stackoverflow.
            s = s.replace(',}','}')
            s = s.replace(',]',']')
            data = json.loads(s)
            #print(json.dumps(data, indent=4,))

        data["User-info"][0]["username"] = information_dict["name"]
        data["User-info"][0]["UUID"] = information_dict["id"]
        data["refreshToken"] = information_dict["refresh_token"]
        data["accessToken"] = information_dict["access_token"]
        data["User-info"][0]["AUTH_TYPE"] = "Microsoft"

        with open("settings.json", "w") as js_write:
            js_write.write(json.dumps(data, indent=4))
            js_write.close()

        message_box = QMessageBox()
        message_box.setWindowTitle("Logged In")
        message_box.setText("You have successfully logged in, {}".format(information_dict["name"]))
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()

        # Exit the program
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # This line sets the language of the webpage to the system language
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name().split("_")[0])
    w = LoginWindow()
    sys.exit(app.exec())
