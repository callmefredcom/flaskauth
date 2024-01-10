# Authentication Boilerplate for Flask

## Presentation

This authentication boilerplate enables you to set up all the authentication logic for username, email, password, as well as Google One  Tap Signup/Login

## Generate key.pem and cert.pem
Required to test the app with local SSL support.<br>
See the end of main.py:

<b>if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))</b>

### Process
Creating self-signed SSL certificates for local development on Windows and macOS can be done using OpenSSL, a powerful open-source toolkit for SSL/TLS. Here's how you can generate key.pem and cert.pem files on both Windows and macOS:

For macOS:
macOS usually comes with OpenSSL pre-installed. You can follow these steps:

Open Terminal: You can find Terminal in Applications > Utilities.

Generate a Private Key:

bash
Copy code
openssl genrsa -out key.pem 2048
Generate a Self-Signed Certificate:

bash
Copy code
openssl req -new -x509 -key key.pem -out cert.pem -days 365
During this process, you will be prompted to enter details like your country, state, organization, etc. These details are used in the certificate's subject field.

For Windows:
Windows does not come with OpenSSL installed, so you'll need to install it first.

Install OpenSSL:

You can download a precompiled version of OpenSSL from here.
Install it on your system.
Open OpenSSL:

You can open it from the Start menu or go to the folder where it's installed and run openssl.exe.
Generate a Private Key:

bash
Copy code
openssl genrsa -out key.pem 2048
Generate a Self-Signed Certificate:

bash
Copy code
openssl req -new -x509 -key key.pem -out cert.pem -days 365
Just like in macOS, you'll be asked to provide some details.

Important Notes:
The -days 365 flag specifies that the certificate will be valid for 365 days. You can adjust this value according to your needs.
Remember, browsers will recognize these certificates as untrusted because they are self-signed. You'll typically see a security warning when you use them, which is fine for local development.
For production environments, you should use a certificate issued by a trusted Certificate Authority (CA).
After these steps, you should have key.pem and cert.pem files ready for use in your local SSL setup.