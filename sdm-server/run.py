# This file is simply a utility file and serves
# as the application entry point.
from sdm_server import app

if __name__ == '__main__':
    app.run(debug=True)