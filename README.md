# Snippit UI
The user interface of Snippit project.

This repo is still under development, feel free to send a bug report.

# Usage
1) Parse the output of profiling. `./scripts/parse.py -i /path/to/output/PID`
2) Enter the folder __public__.
3) Open an simple http server in the folder __public__. `python3 -m http.server`
4) Use your web browser to open `http://127.0.0.1:8000/`

# Example
``` bash
./scripts/parse.py -i /tmp/snippit/phase/740
cd ./public && python3 -m http.server
```

