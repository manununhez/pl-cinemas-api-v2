import sys
from importlib import import_module

sys.path.append('/home/yvyty/pl-cinemas-api-v2')

app_module = import_module('app')
app = app_module.app

if __name__ == "__main__":
    app.run()
