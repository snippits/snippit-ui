# Snippit UI
The user interface of Snippit project.
![Image of Snippit](/images/snippit.png?raw=true "Sample Image")

This repo is still under development, feel free to send a bug report.

# Usage
1. Open the server to load your Snippits output. `./script/server.py` (Default: /tmp/snippits)
2. Use your web browser to open `http://127.0.0.1:5000/`

# Important Note on Code Mapping
* If your application does not contain DWARF (i.e. gcc -g), the Code section might be blank.
* Please compile your program with `-g` flag to enjoy the code mapping.
* The current version does not search for file, it uses the absolute path to locate the file.
You must compile the binary on your machine in order to make code mapping work.

# Development Mode of source code
```
npm install
npm run watch
```

# Running the server (Flask)
Install all the dependencies
```
pip3 install flask flask-script Flask-Sockets
```
Run it by `./script/server.py`
