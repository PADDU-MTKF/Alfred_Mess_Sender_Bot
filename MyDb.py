import sqlite3


def create_table(DB, TABLE_NAME, COL_LIST):
    """
    COL_LIST=[
                {'col_name':'col_1', 'col_type':'int','extra':'primary key not null'}, # extra is full command
                {'col_name':'col_2', 'col_type':'text'}
             ]
    """

    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    cmd = ""
    count = 0
    for row in COL_LIST:
        count += 1
        cmd += f"{row['col_name']} {row['col_type']} "
        if 'extra' in row:
            cmd += f"{row['extra']} "
        if count != len(COL_LIST):
            cmd += ','

    try:
        cursor.execute(f"CREATE TABLE {TABLE_NAME} ({cmd})")
        result = True
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


def add_data(DB, TABLE_NAME, DATA_LIST, flag=0):
    """
    DATA_LIST=  [
                (value1,value2),
                (value1,value2),
                (value1,value2)
                ]
    """
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    try:
        for data in DATA_LIST:
            if flag == 0:
                cursor.execute(f"INSERT INTO {TABLE_NAME} VALUES {data}")
            else:
                cursor.execute(f"""INSERT INTO {TABLE_NAME} VALUES (?,?,?,?,?,?,?,?,?);""", (
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
        mydb.commit()
        result = True
    except Exception as e:
        result = e

    mydb.close()
    return result


def get_all(DB, TABLE_NAME, COL='*'):
    """
    COL='regno'
    COL='regno,name,class'
    """
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    try:
        cursor.execute(f"SELECT {COL} FROM {TABLE_NAME}")
        result = cursor.fetchall()
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


def get_one(DB, TABLE_NAME, WHICH, COL='*'):
    """
    WHICH = "rgno=52"
    WHICH = "name='df' and lname='d'"

    COL="rgno"
    COL="rgno,name"
    """
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    try:
        cursor.execute(f"SELECT {COL} FROM {TABLE_NAME} WHERE {WHICH}")
        result = cursor.fetchall()
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


def update(DB, TABLE_NAME, WHAT, WHICH=''):
    """
    WHAT = "regno=44"
    WHAT = "regno=4,name='new'"

    WHICH ="regno=55"
    WHICH ="regno=88 and name='class'"
    """
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    if WHICH != '':
        WHICH = "WHERE "+WHICH
    try:
        cursor.execute(f"UPDATE {TABLE_NAME} SET {WHAT} {WHICH}")
        result = cursor.fetchall()
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


class alter():
    def add_col(DB, TABLE_NAME, COL_LIST):
        """
        COL_LIST=[
                    {'col_name':'col_1', 'col_type':'int','extra':'primary key not null'}, # extra is full command
                    {'col_name':'col_2', 'col_type':'text'}
                 ]
        """

        mydb = sqlite3.connect(DB)
        cursor = mydb.cursor()
        cmd_list = []
        for row in COL_LIST:
            cmd = ""

            cmd += f"{row['col_name']} {row['col_type']} "
            if 'extra' in row:
                cmd += f"{row['extra']} "

            cmd_list.append(cmd)

        for cmd in cmd_list:
            try:
                cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {cmd}")
                result = True
            except Exception as e:
                result = e
                break
        if result == True:
            mydb.commit()
        mydb.close()
        return result

    def rename_table(DB, TABLE_NAME, NEW):
        mydb = sqlite3.connect(DB)
        cursor = mydb.cursor()
        try:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} RENAME TO {NEW}")
            result = True
        except Exception as e:
            result = e

        mydb.commit()
        mydb.close()
        return result

    def rename_col(DB, TABLE_NAME, OLD, NEW):
        mydb = sqlite3.connect(DB)
        cursor = mydb.cursor()
        try:
            cursor.execute(
                f"ALTER TABLE {TABLE_NAME} RENAME COLUMN {OLD} TO {NEW}")
            result = True
        except Exception as e:
            result = e

        mydb.commit()
        mydb.close()
        return result

    def drop_col(DB, TABLE_NAME, COL):
        mydb = sqlite3.connect(DB)
        cursor = mydb.cursor()
        try:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} DROP COLUMN {COL}")
            result = True
        except Exception as e:
            result = e

        mydb.commit()
        mydb.close()
        return result


def delete(DB, TABLE_NAME, WHICH=''):
    """
    WHICH ="regno=55"
    WHICH ="regno=88 and name='class'"
    """
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    if WHICH != '':
        WHICH = "WHERE "+WHICH
    try:
        cursor.execute(f"DELETE FROM {TABLE_NAME} {WHICH}")
        result = cursor.fetchall()
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


def drop_table(DB, TABLE_NAME):
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    try:
        cursor.execute(f"DROP TABLE {TABLE_NAME}")
        result = cursor.fetchall()
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


def desc(DB, TABLE_NAME):
    mydb = sqlite3.connect(DB)
    cursor = mydb.cursor()
    try:
        cursor.execute(f"PRAGMA table_info ({TABLE_NAME})")
        head = ("cid", "name", "type", "notnull", "dflt_value", "primary key")
        result = []
        result.append(head)
        result.extend(cursor.fetchall())
    except Exception as e:
        result = e

    mydb.commit()
    mydb.close()
    return result


COL_LIST = [
    {'col_name': 'ggdfg', 'col_type': 'int', 'extra': 'default 0 not null'},
    {'col_name': 'dgdgd', 'col_type': 'text'},
    {'col_name': 'gdfdk', 'col_type': 'text'}
]


DATA_LIST = [
    (10, 'paddu', 'BCA'),
    (14, 'pradyumna', 'bbca'),
    (1, 'hacked', 'HACKER')
]

# print(create_table(DB='passwd.db',TABLE_NAME='student',COL_LIST=COL_LIST))

# print(add_data(DB='passwd.db',TABLE_NAME='student',DATA_LIST=DATA_LIST))

# print(desc(DB='passwd.db',TABLE_NAME='student'))


# print(get_one(DB='passwd.db',TABLE_NAME='student',WHICH="regno=1",COL='name'))

# print(update(DB='passwd.db',TABLE_NAME='student',WHAT="regno=12",WHICH="regno=1"))

# print(alter.add_col(DB='passwd.db',TABLE_NAME='student',COL_LIST=COL_LIST))

# print(alter.rename_table(DB='passwd.db',TABLE_NAME='stu',NEW='student'))

# print(alter.drop_col(DB='passwd.db',TABLE_NAME='student',COL='qwertty'))

# print(alter.rename_col(DB='passwd.db',TABLE_NAME='student',OLD='ggdfg',NEW='qwertty'))

# print(delete(DB='passwd.db',TABLE_NAME='student',WHICH='regno=10'))

# print(drop_table(DB='passwd.db',TABLE_NAME='student'))
# print(get_all(DB='passwd.db',TABLE_NAME='student',COL='*'))
