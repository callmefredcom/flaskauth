# Authentication Boilerplate for Flask

## Presentation

This authentication boilerplate enables you to set up all the authentication logic for username, email, password, as well as Google One  Tap Signup/Login.

You can fork it and adapt the content of the **/app** page with your own logic.

Do not forget to create a **.env** file with all your secret keys.

This demo is using a MySQL database on Railway (https://railway.app)

```python 
db_password = os.environ.get('MYSQL_PASSWORD')

# MySQL configuration
DATABASE_URL = f"mysql -roundhouse.proxy.rlwy.net -uroot -p{db_password} --port 35429 --protocol=TCP railway"

DATABASE_CONFIG = {
            'user': 'root',
            'password': os.environ.get('MYSQL_PASSWORD'),
            'host': 'roundhouse.proxy.rlwy.net',
            'port': '35429',
            'database': 'railway'
        }

def get_db():
    if hasattr(g, 'db_conn') and g.db_conn.is_connected():
        return g.db_conn
    else:
        g.db_conn = mysql.connector.connect(**DATABASE_CONFIG)
        return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db_conn', None)
    if db is not None:
        db.close()

```

If you're using Railway, you'll have to adapt the connection details in main.py and add your own password in your .env file.

This demo is using Brevo (ex SendInBlue, https://brevo.com) to send transactional emails via the emails.py file.
You're free to either repurpose the same logic with your own API key or use another provider. 

```python
# Set up the API key and endpoint
api_key = os.environ.get('SENDINBLUE')
url = "https://api.sendinblue.com/v3/smtp/email"
```

## Register your service via the Google Cloud Console to use Google Login

Go to the Google Cloud Console.<br>
https://cloud.google.com/cloud-console

+ Create a new project.<br>
+ Navigate to "APIs & Services" > "Credentials".<br>
+ Click on "Create Credentials" and select "OAuth client ID".<br>
+ Set the application type to "Web application".<br>
+ Add the authorized redirect URI, which will be http://127.0.0.1:5000/login/google/authorized if you're testing locally.<br>

+ Note down the Client ID and Client Secret.

## Generate key.pem and cert.pem
Those 2 files are required to test the app with local SSL support.<br>
See the end of main.py:

```python 
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem')) 
```

### Process
Creating self-signed SSL certificates for local development on Windows and macOS can be done using OpenSSL, a powerful open-source toolkit for SSL/TLS. Here's how you can generate key.pem and cert.pem files on both Windows and macOS:

#### For macOS:
macOS usually comes with OpenSSL pre-installed. You can follow these steps:

Open Terminal: You can find Terminal in Applications > Utilities.

#### Generate a Private Key:

```bash
openssl genrsa -out key.pem 2048
```

#### Generate a Self-Signed Certificate:
```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

During this process, you will be prompted to enter details like your country, state, organization, etc. These details are used in the certificate's subject field.

#### For Windows:

Windows does not come with OpenSSL installed, so you'll need to install it first.

Install OpenSSL:

You can download a precompiled version of OpenSSL from https://slproweb.com/products/Win32OpenSSL.html

Install it on your system.

Open OpenSSL:

You can open it from the Start menu or go to the folder where it's installed and run openssl.exe.

#### Generate a Private Key:
```bash
openssl genrsa -out key.pem 2048
```
#### Generate a Self-Signed Certificate:
```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

Just like in macOS, you'll be asked to provide some details.

### Important Notes:

#### OpenSSL on Windows

On Windows, you may face the following error the first time you run the openssl command to generate your private key: 
```python
The term 'openssl' is not recognized as the name of a cmdlet, function, script file, or operable program. Check the spelling of the name, or if a path was included, 
verify that the path is correct and try again.
At line:1 char:1
+ openssl genrsa -out key.pem 2048
+ ~~~~~~~
    + CategoryInfo          : ObjectNotFound: (openssl:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```
Here is the solution: 

The error you're encountering in PyCharm indicates that the openssl command is not recognized in your Windows environment. This usually happens if the OpenSSL executable is not in your system's PATH environment variable. Here's how you can fix this:

Locate OpenSSL Installation Directory: First, you need to find out where OpenSSL is installed on your system. The installation directory will have openssl.exe in it. If you installed OpenSSL using a standard installer, it's often located in a directory like C:\Program Files\OpenSSL-Win64\bin or C:\OpenSSL-Win32\bin.

Add OpenSSL to the System PATH:

+ Right-click on 'This PC' or 'My Computer' on your desktop or in File Explorer.
+ Click 'Properties'.
+ Click 'Advanced system settings'.
+ In the System Properties window, go to the 'Advanced' tab and click 'Environment Variables'.
+ In the Environment Variables window, under 'System variables', find and select the 'Path' variable, then click 'Edit'.
+ In the Edit Environment Variable window, click 'New' and add the path to the OpenSSL bin directory (e.g., C:\Program Files\OpenSSL-Win64\bin).
+ Click 'OK' to close each window.
+ Restart PyCharm or Your System: After adding OpenSSL to your system's PATH, you may need to restart PyCharm or your computer for the changes to take effect.

Verify the OpenSSL Installation:

+ Open a new command prompt (not PyCharm's terminal, but a separate Windows command prompt).
+ Type **openssl version** and press Enter.

+ If OpenSSL is correctly installed and added to your PATH, you should see the version information of OpenSSL.
Run the OpenSSL Command Again: After confirming that OpenSSL is recognized in the command prompt, try running your command (openssl genrsa -out key.pem 2048) again in PyCharm's terminal.

#### Obfuscator.py requires a npm package: javascript-obfuscator 

To make this code work, you'll need to ensure that you have the following prerequisites installed and set up:

Node.js: Make sure you have Node.js installed on your system. You can download and install it from the official website: https://nodejs.org/

javascript-obfuscator package: You need to install the javascript-obfuscator package globally or locally in your project. You can do this using npm (Node Package Manager). Run the following command to install it globally:

```bash
npm install -g javascript-obfuscator
```

Alternatively, you can install it locally within your project by running the following command in your project directory:

```bash
npm install javascript-obfuscator
```

Ensure that the npm and npx commands are available in your terminal after installing Node.js. These commands are required to install and run Node.js packages, including javascript-obfuscator.

Confirm that your system's PATH environment variable includes the location where globally installed Node.js packages are stored. This is typically found in the node_modules folder in your user directory (e.g., C:\Users\<YourUsername>\AppData\Roaming\npm on Windows).

After you have installed Node.js and the javascript-obfuscator package, and you've made sure that npm and npx are available in your terminal, you should be able to run obfuscator.py successfully to obfuscate your JavaScript file.