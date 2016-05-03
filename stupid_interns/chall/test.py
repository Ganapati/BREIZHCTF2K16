from bottle import route, run, template, request, response
from Crypto.Cipher import DES3
import base64
import sqlite3

conn = sqlite3.connect('users.db')
key = "FOOBARBAZGU01234"

def attack(viewstate):
    """ Help for testing
    """
    input = base64.b64decode(viewstate)
    input_splitted = [input[i:i+8] for i in range(0, len(input), 8)]
    input_splitted[0], input_splitted[4] = input_splitted[4], input_splitted[0]
    shuffle = ''.join(input_splitted)
    payload = base64.b64encode(shuffle)
    print "(%s)" % uncipher(payload, key)
    print payload

"""
Crypto part
"""

def cipher(clear, key):
    pad_len = 8 - len(clear) % 8 # length of padding
    padding = chr(pad_len) * pad_len # PKCS5 padding content
    clear += padding
    cipher = DES3.new( key, DES3.MODE_ECB )
    return base64.b64encode(cipher.encrypt(clear))

def uncipher(cipher, key):
    uncipher = DES3.new( key, DES3.MODE_ECB )
    clear = uncipher.decrypt(base64.b64decode(cipher))
    padding = clear[-1]
    return clear[:-ord(padding)]


def parse_data(clear):
    clear = clear.replace(' ', '')
    clear = clear.replace('"', '')
    step1 = clear.split("|")
    step2 = {}
    for item in step1:
        try:
            k, v = item.split(":")
            step2[k] = v
        except:
            pass
    return step2

def valid_viewstate(viewstate):
    if viewstate is None:
        return False
    try:
        data = parse_data(viewstate)
    except:
        return False
    return ("_id_" in data.keys() and "on" in data.keys() and "p" in data.keys() and data['on'] != '0')

"""
DB section
"""

def login(login, password):
    t = (login, password)
    c.execute('SELECT * FROM users WHERE login=? AND password=?', t)
    data = c.fetchone()
    if data is not None and data[1] == 1:
        return {"_id_": data[0], "on":1, "p":1}
    else:
        return {"_id_": 0, "on":0, "p":1}

def print_infos(id):
    id = id.replace('+', ' ')
    req = 'SELECT login, active FROM users WHERE id=%s' % id
    c.execute(req)
    data = c.fetchone()
    if data is not None:
        if data[1] == 1:
            return data[0]
        else:
            return "User disabled"
    else:
        return ""

"""
Web part
"""

@route('/')
@route('/<page>', method=["POST", "GET"])
def page(page='0'):
    viewstate = request.get_cookie("VIEWSTATE")
    content = ""
    error_log = ""
    if viewstate is not None:
        try:
            viewstate_clear = uncipher(viewstate, key)
        except:
            error_log = "Error unciphering viewstate"
    else:
        viewstate_clear = {"_id_": 0, "p":1, "on":0}

    # Check session
    try:
        viewstate_parsed = parse_data(viewstate_clear)
        user_info = '|"_id_":   "%s" |"on"  :   %s|   "p":      "%s"' % (viewstate_parsed["_id_"],
                                                                      viewstate_parsed["on"],
                                                                      page)
    except:
        error_log = "Error parsing viewstate"
        user_info = '|"_id_":   0    |"on"  :   0  |  "p":      "%s"' % page
    
    user_data = parse_data(user_info)
    new_viewstate = cipher(user_info, key)
    response.set_cookie("VIEWSTATE", new_viewstate)

    if page == '0':
        # DISPLAY LOGIN FORM

        name = request.forms.get('login')
        password = request.forms.get('password')
        if name is not None and password is not None:
            log = login(name, password)
            if log['_id_'] != 0 :
                user_info = '|"_id_":   %s    |"on"  :   %s  |  "p":      "%s"' % (log["_id_"], 
                                                                                   log["on"],
                                                                                   log["p"])
                new_viewstate = cipher(user_info, key)
                response.set_cookie("VIEWSTATE", new_viewstate)
                content = "LOGIN SUCCESS"
            else:
                content = "LOGIN FAILED"
        else:
            content= '''
            <form action="/0" method="post" class="form-horizontal">
                Username : <input type="text" name="login" class="form-control"/><br />
                Password: <input type="password" name="password" class="form-control"/><br />
                <input type="submit" value="Login" class="btn btn-default"/>
            </form>
            '''
    elif page == '1':
        # DISPLAY WELCOME USER
        if not valid_viewstate(viewstate_clear):
            content = "Logged users only !"
        else:
            content = "WELCOME"
    elif page == '2':
        # DISPLAY USER INFOS
        if not valid_viewstate(viewstate_clear):
            content = "Logged users only !"
        else:
            # return user_info
            try:
                name = print_infos(user_data["_id_"])
            except:
                name = "Error in SQL syntax"
            content = "username : %s" % name
    elif page == '3':
        # LOGOUT
        if not valid_viewstate(viewstate_clear):
            content = "Logged users only !"
        else:
            user_info = '|"_id_":   0    |"on"  :   0   | "p":   0'
            new_viewstate = cipher(user_info, key)
            response.set_cookie('VIEWSTATE', new_viewstate)
            content = "LOGOUT"
    else:
        # DISPLAY 404
        attack(viewstate)
        content =  "page introuvable"
    return template("main", {"content": content, "error":error_log})

"""
Setup / Start
"""

if __name__ == "__main__":

    c = conn.cursor()
    c.execute('''DROP TABLE users''')
    c.execute('''CREATE TABLE users
                         (id int, active int, login text, password text)''')
    c.execute("INSERT INTO users VALUES (2,1,'demo','demo')")
    c.execute("INSERT INTO users VALUES (1,0,'admin','BZHCTF{B4DCrypt0}')")
    conn.commit()
    #clear = '"_id_" :   2    |"on"  :   1   | "p":   2'
    #print cipher(clear, key)
    run(host='0.0.0.0', port=8080)
