# CMSC495
Repository for the CMSC495 Simple Drink Maker project.

# Setup for development and testing
## Frontend
Running the SDM frontend requires Node and NPM, which is automatically installed alongside Node.

Node can be installed from: https://nodejs.org/en/

Follow your operating sysystem sepcific instructions to install Node.

Once Node is installed, navigate to your local repository base and run the following commands to start the frontend:

```
cd CMSC495/sdm-ui     //Navigate to the root of the application.
npm i                 //Install application dependencies.
npm start             //Launch the development server.
```

The frontend should automatically start in your browser. If it doesn't, open your browser and navigate to:
```
http://localhost:3000/
```

## Backend
Running the SDM backend in development requires Python 3.6.x, and several dependencies which will be installed.

Python 3 can be installed from: https://www.python.org/downloads/

Follow your operating system specific instructions to install Python 3, to at least 3.6.x. The SDM backend currently uses Python 3.6.9.

Once Python is installed, navigate to your local repository base and run the following commands to start the backend:

### POSIX-based OS
```
cd CMSC495/sdm-server/sdm_server
python3 -m venv env
source env/bin/activate
```

### Windows
```
cd CMSC495\sdm-server\sdm_server
python3 -m venv c:\path\to\CMSC495\env\
c:\path\to\CMSC495\env\Scripts\activate.bat
```

Once the Python virtual environment is activated the dependencies included in requirements.txt can be installed. Before proceeding, open the requirements.txt file and remove the lines:
```
mysqlclient==1.4.6
pkg-resources==0.0.0
```
These dependencies are required to run MySQL in the production environment, however, installation will fail if MySQL Server is not properly configured on the development host machine. The development backend uses SQLite for simplicity so the dependencies can be removed in development.

After those lines are removed, make sure the virtual environment is activated and run the following commands:

```
cd CMSC495/sdm-server
pip3 install -r ./requirements.txt
python3 run.py
```

The SDM backend should now be running and application development/testing can begin.
