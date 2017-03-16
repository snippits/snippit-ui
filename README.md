# Snippit UI
The user interface of Snippit project.
![Image of Snippit](/images/snippit.png?raw=true "Sample Image")

This repo is still under development, feel free to send a bug report.

# Usage
1. Parse the output of profiling. `./scripts/parse.py -i /path/to/output/PID`
2. Enter the folder __public__.
3. Open an simple http server in the folder __public__. `python3 -m http.server`
4. Use your web browser to open `http://127.0.0.1:8000/`

# Important Note on Code Mapping
* If your application does not contain DWARF (i.e. gcc -g), the Code section might be blank.
* Please compile your program with `-g` flag to enjoy the code mapping.
* The current version does not search for file, it uses the absolute path to locate the file.
You must compile the binary on your machine in order to make code mapping work.

# Example
``` bash
./scripts/parse.py -i /tmp/snippit/phase/740
cd ./public && python3 -m http.server
```

# Development Mode of source code
```
npm install
npm run dev
```

