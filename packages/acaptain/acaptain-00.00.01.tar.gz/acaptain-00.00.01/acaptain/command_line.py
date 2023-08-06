import acaptain
def main():         #Use to spawn the overall system
    acaptain.main()
def dbstartup():    #start the local database client
    print("starting dbclient!")
    acaptain.db()
def ssstartup(): #start the sensor server
    print("starting up arduino!")
    acaptain.ss()
def uistartup(): #Start flask
    print("starting flask!")
    acaptain.ui()
