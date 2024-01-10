# Authentication Boilerplate for Flask

## Presentation

This authentication boilerplate enables you to set up all the authentication logic for username, email, password, as well as Google One  Tap Signup/Login.

You can fork it and adapt the content of the **/app** page with your own logic.

Do not forget to create a **.env** file with all your secret keys.

This demo is using a MySQL database on Railway. 

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

This demo is using Brevo (ex SendInBlue) to send transactional emails via the emails.py file.
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
+ Add the authorized redirect URI, which will be http://localhost:5000/login/google/authorized if you're testing locally.<br>

**+ Note down the Client ID and Client Secret.**

## Generate key.pem and cert.pem
Required to test the app with local SSL support.<br>
See the end of main.py:

```python 
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem')) 
```

### Process
Creating self-signed SSL certificates for local development on Windows and macOS can be done using OpenSSL, a powerful open-source toolkit for SSL/TLS. Here's how you can generate key.pem and cert.pem files on both Windows and macOS:

For macOS:
macOS usually comes with OpenSSL pre-installed. You can follow these steps:

Open Terminal: You can find Terminal in Applications > Utilities.

#### Generate a Private Key:

```bash
openssl genrsa -out key.pem 2048
Generate a Self-Signed Certificate:
```


```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

During this process, you will be prompted to enter details like your country, state, organization, etc. These details are used in the certificate's subject field.

For Windows:
Windows does not come with OpenSSL installed, so you'll need to install it first.

Install OpenSSL:

You can download a precompiled version of OpenSSL from here.
Install it on your system.

Open OpenSSL:

You can open it from the Start menu or go to the folder where it's installed and run openssl.exe.
Generate a Private Key:

```bash
openssl genrsa -out key.pem 2048
Generate a Self-Signed Certificate:
```

```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

Just like in macOS, you'll be asked to provide some details.

Important Notes:

The -days 365 flag specifies that the certificate will be valid for 365 days. You can adjust this value according to your needs.
Remember, browsers will recognize these certificates as untrusted because they are self-signed. You'll typically see a security warning when you use them, which is fine for local development.
For production environments, you should use a certificate issued by a trusted Certificate Authority (CA).
After these steps, you should have key.pem and cert.pem files ready for use in your local SSL setup.