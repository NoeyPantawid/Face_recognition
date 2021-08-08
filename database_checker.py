import os, sqlite3

try:
    connect = sqlite3.connect(os.getcwd() + '\\database\\db.sqlite')
    cur = connect.cursor()
    sql_cmd = "SELECT * FROM People"

    counter = 0
    for row in cur.execute(sql_cmd):
        print("============ row {} ============".format(counter+1))
        print("ID , NAME , TIER")
        print(row)
        counter += 1

except:
    print('No database found!')