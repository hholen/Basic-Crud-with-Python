import sqlite3 as sqlite
import os, datetime, time

USER = None

### Helper functions
def clearit():
    """this function clears the terminal window to make it all pretty"""
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')

def maketime(n):
    """Convert a unix timestamp to a readable time format"""
    return datetime.datetime.fromtimestamp(n).strftime('%d/%m/%Y - %H:%M:%S')

def return_to_main():
    raw_input("Press any key to continue.")
    clearit()
    main()


#### The following functions control our database access.
#### This is the core of our CRUD system
DBconn = sqlite.connect(':memory:') #':memory:' means it resets each time you start
DBconn.row_factory = sqlite.Row
cursor = DBconn.cursor()

def create_db():
    """This function creates a database if it doesn't exist """
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                 (ID integer primary key, user text, note text,
                  created integer, last_edited integer) ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (username text primary key, password text)''')
    DBconn.commit()

def create_user(un, pw):
    cursor.execute('INSERT INTO users VALUES (?, ?)', (un, pw))
    DBconn.commit()
    return login

def retrieve_user(un,pw):
    check_user = cursor.execute('SELECT * FROM users where username = ? AND password = ?', (un,pw))
    if check_user:
        global USER
        USER = check_user.fetchone()[0]
        main()
    if not check_user:
        return "Username or password is wrong"


def create(note):
    """ Adds data to our database """
    cursor.execute('INSERT INTO notes VALUES (null, ?, ?, ?, ?)', (note, USER, time.time(), time.time()))
    DBconn.commit()
    return "Sucessfully added!"

def retrieve(n=""):
    """Retrieve data"""
    if n == "":
        return cursor.execute('SELECT ID, note FROM notes')        
    else:
        n = str(n)
        cursor.execute('SELECT * FROM notes where ID = ?', n)
        return cursor.fetchone()

def update(text,id):
    """Update a note in the database"""
    cursor.execute('UPDATE notes SET note = ?, last_edited = ? WHERE ID = ?', (text, time.time(), id))
    DBconn.commit()
    return "Sucessfully updated note."

def delete(n):
    """Delete a note in the database"""
    cursor.execute('DELETE FROM notes WHERE id = ?', str(n))
    DBconn.commit()
    return "Deleting note."

#### Let's create the interface for our notepad.
#### You'll notice that we've separated user input from database access
def ui():
    """This is the main UI element"""
    clearit()
    print "Welcome to your Notepad, %s." % USER
    print "Your notes"
    all_notes = retrieve()
    try:
        first_row = all_notes.next()
        for row in [first_row] + all_notes.fetchall():
            print "\t%s: %s" % (row[0], row[1])
        print "\n"
    except StopIteration as e:
        print "\n\tNo entries\n"
    print "Please select your action:"
    print """\t(C)reate a note, (R)etrieve a note,
    \t(U)pdate a note or (D)elete a note"""
    return raw_input("What would you like to do? >> ").lower()

def input(action):
    """This UI element lets you pick the item you want to edit"""
    selections = {'r': 'retrieve','u':'update', 'd': 'delete'}
    functions = {'r': retrieve_ui,'u':update_ui, 'd': del_ui}
    choice = raw_input("Please chose the ID of the note you want to %s. >> " \
                        % selections[action])
    try: # Now let's make sure they picked an ID number i.e. an integer.
        functions[action](int(choice))
    except ValueError: #if it's not an integer, we'll get an error 
        print "Please pick an ID number."
        input(action)

def login():
    clearit()
    print "Please log in: \n"
    un = raw_input("Username: ")
    pw = raw_input("Password: ")
    print retrieve_user(un,pw)
    login()

def signup():
    un = raw_input("Pick a Username: ")
    pw = raw_input("Pick a Password: ")
    result = create_user(un,pw)
    raw_input("Sucessfully added user. Press any key to continue")
    result()

def create_ui():
    """this is the UI element that uses the create function"""
    note = raw_input('Add your note. >> ')
    print create(note)
    return_to_main()

def retrieve_ui(id):
    """this is the UI element that uses the retrieve function"""
    result = retrieve(id)
    if not result:
        print "No entries"
    else:
        print "%s: %d: %s, %s %s" % (result[1], result[0],result[2], maketime(result[3]),maketime(result[4]))
    return_to_main()

def update_ui(id):
    """this is the UI element that uses the update function"""
    result = retrieve(id)
    if not result:
        print "No entries"
        return_to_main()
    else:
        edited_note = raw_input("What is the new note text? >> ")
        print update(edited_note, id)
        return_to_main()

def del_ui(id):
    """This UI element controls deletion. """
    object_to_delete = cursor.execute('SELECT note FROM notes where id = ?', str(id)).fetchone()
    if object_to_delete is not None:
        choice = raw_input("Are you sure you want to delete '%s'? Y/N >> " % object_to_delete[0]).lower()
        if choice == 'y':
            print delete(id)
            return_to_main()
        if choice == 'n':
            print "aborting."
            return_to_main()
        else:
            raw_input("Unknown input. Press any key to continue")
            del_ui(id)
    else:
        print "Nothing to delete."
        return_to_main()

def main():
    if USER is None:
        clearit()
        print "Welcome to Notepad.\n"
        response =raw_input("(L)og in or (S)ign up to continue. ")
        if response.lower() == 'l':
            login()
        elif response.lower() == 's':
            signup()
        else:
            print "You need to pick L or S."
            return_to_main()
    else:
        # Take the user's choice and put it in a variable
        action = ui()
        # Send them to the correct UI function
        if action == "r" or action == "u" or action == "d":
            input(action)
        elif action == 'c':
            create_ui()
        # The user needs to pick C, R, U or D
        else:
            print "That's not a valid input."
            raw_input("Press any key to continue.")
            main()

create_db()
main()