import Menu
import getpass
import hashlib
import sqlite3
from pathlib import Path
# import random
import datetime
from Task import Task

# import matplotlib
# import matplotlib.pyplot as plt
import random
import time

# current_milli_time = lambda: int(round(time.time() * 1000))

user_id = 0


def get_input(text, input_type, not_null=True, greater_than=(), less_than=(), allowed_values=()):
    answer = None
    done = False
    while not done:
        answer = input(text)
        done = True
        try:
            answer = input_type(answer)
        except:
            done = False
            continue
        if not_null and (answer == None or answer == ""):
            done = False
            continue
        if greater_than:
            if answer <= greater_than[0]:
                done = False
                continue
        if less_than:
            if answer >= less_than[0]:
                done = False
                continue
        if allowed_values and (answer not in allowed_values):
            done = False
            continue
    return answer


def first_run():
    print("Please be patient... setting up database.")
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute('''

    CREATE TABLE User 
    (
    user_id         INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_name       VARCHAR(30) NOT NULL UNIQUE,
    user_salt       VARCHAR(30) NOT NULL,
    user_pw_hash    VARCHAR(30) NOT NULL
    )

    ''')

    c.execute('''

    CREATE TABLE Category
    (
    category_id         INTEGER     PRIMARY KEY AUTOINCREMENT,
    category_name       VARCHAR(30) NOT NULL,
    category_importance INTEGER     NOT NULL
    )

    ''')

    c.execute('''

    CREATE TABLE Task
    (
    task_id                     INTEGER     PRIMARY KEY AUTOINCREMENT,
    created_by                  INTEGER     NOT NULL,
    category_id                 INTEGER     NOT NULL,
    task_text                   VARCHAR(30) NOT NULL,
    task_due_date               REAL        NOT NULL,
    task_interval               REAL        NOT NULL,
    task_importance             INTEGER     NOT NULL,
    task_postpone               REAL        NOT NULL,
    allow_early_completion      VARCHAR(30) NOT NULL    CHECK(allow_early_completion IN ('y', 'n')),
    FOREIGN KEY(created_by)     REFERENCES  User(user_id),
    FOREIGN KEY(category_id)    REFERENCES  Category(category_id)
    )

    ''')

    conn.commit()
    c.close()
    conn.close()


def verify_login_and_get_id(login_uname, login_password):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute('''SELECT user_salt FROM User
                 WHERE user_name = ?''', [login_uname])

    salt = c.fetchone()

    if salt:
        salt = salt[0]
    else:
        print("Incorrect username or password.")
        return -1

    c.execute('''

    SELECT user_id FROM User
    WHERE user_name = ?
    AND user_pw_hash = ?''',
              [login_uname, str(hashlib.sha3_256((login_password + login_uname + salt).encode('utf-8')).hexdigest())])

    login_password = '0'
    user_id = c.fetchone()

    c.close()
    conn.close()

    if user_id:
        return user_id[0]
    else:
        print("Incorrect username or password.")
        return -1


def try_log_in(options):
    global user_id
    user_name = get_input("Username: ", str)
    password = ""
    password = getpass.getpass("Password: ")
    user_id = verify_login_and_get_id(user_name, password)
    password = '0'
    if user_id > 0:
        options[0].display(None)


def create_user(options):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    valid_user_name_found = False
    new_user_name = ''
    while not valid_user_name_found:
        for i in range(100):
            print()
        new_user_name = get_input("New Username: ", str)
        if new_user_name == "":
            continue
        c.execute('''

        SELECT user_name FROM User
        WHERE user_name = ?

        ''', (new_user_name,))
        found = c.fetchone()
        if found:
            print("This username is already in use.")
            continue
        else:
            valid_user_name_found = True

    password = getpass.getpass("Password: ")

    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(random.choice(alphabet))
    salt = "".join(chars)
    c.execute('''

    INSERT INTO User
    (user_name, user_salt, user_pw_hash)
    VALUES (?, ?, ?)

    ''', (new_user_name, salt, str(
        hashlib.sha3_256((password + new_user_name + salt).encode('utf-8')).hexdigest())))
    password = '0'

    conn.commit()
    c.close()
    conn.close()


def get_categories():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

            SELECT category_id, category_name, category_importance FROM category

            ''')
    categories = c.fetchall()
    c.close()
    conn.close()
    return categories


def get_tasks():
    global user_id
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

            SELECT t.task_id, t.category_id, c.category_importance, t.task_text, t.task_due_date, t.task_importance, t.allow_early_completion, t.task_interval, t.task_postpone
            FROM Task t INNER JOIN Category c
            ON t.category_id = c.category_id
            WHERE   created_by = ?

            ''', [user_id])
    tasks = c.fetchall()
    task_objects = []
    for task in tasks:
        task_object = Task(task[0], task[1], task[3], task[4], task[7], task[5], task[8], task[6], task[2])
        task_objects.append(task_object)
    c.close()
    conn.close()
    return task_objects


def choose_category():
    categories = get_categories()
    category_menu = Menu.Menu()
    for category in categories:
        category_menu.add_option(category[1], lambda a: a, category[0])
    return category_menu.display(["exit_on_choose"])


def add_task(options):
    categories = get_categories()
    if not categories:
        print("There are no categories to add the task to. Please add a category first.")
        return
    task_text = get_input("What is the task? ", str)
    print("What category does the task belong to?")
    task_category = choose_category()
    task_importance = get_input("How important is this task to that category? ", int, greater_than=(0,), less_than=(11,))
    year_due = get_input("Year the task is due: ", int)
    month_due = get_input("Month the task is due (1-12): ", int, greater_than=(0,), less_than=(13,))
    day_due = get_input("Day the task is due: ", int, greater_than=(0,), less_than=(32,))
    hour_due = get_input("Hour the task is due: ", int, greater_than=(-1,), less_than=(25,))
    minute_due = get_input("Minute the task is due: ", int, greater_than=(-1,), less_than=(61,))
    date_due = datetime.date(int(year_due), int(month_due), int(day_due))
    date_due = date_due.toordinal()
    date_due += int(hour_due) / 24
    date_due += int(minute_due) / (24 * 60)
    rep_interval = get_input("Number of days between repetitions: ", int, greater_than=(-1,))
    allow_completion_before_due = get_input("Allow completion before due date (y/n): ", str, allowed_values=('y', 'n'))

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

                    INSERT INTO Task
                    (created_by, category_id, task_text, task_due_date, task_interval, allow_early_completion, task_importance, task_postpone)
                    VALUES
                    (?,?,?,?,?,?,?,0)

                    ''', (user_id, task_category, task_text, date_due,
                          rep_interval, allow_completion_before_due, task_importance))
    conn.commit()
    c.close()
    conn.close()


def add_category(options):
    cat_name = get_input("What is the name of the new category?", str)
    cat_importance = get_input("From 1 to 10, what is the importance of the category to your overall well-being?",
                               int, greater_than=(0,), less_than=(11,))
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

                INSERT INTO category
                (category_name, category_importance)
                VALUES
                (?,?)

                ''', (cat_name, cat_importance))
    conn.commit()
    c.close()
    conn.close()


def change_category_name(category):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    
    UPDATE Category
    SET category_name = ?
    WHERE category_id = ?
    
    ''', [input("What is the new name of the category? "), category[0]])
    conn.commit()
    c.close()
    conn.close()


def change_task_text(task):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

    UPDATE Task
    SET task_text = ?
    WHERE task_id = ?

    ''', [input("What is the new name of the task? "), task.id])
    conn.commit()
    c.close()
    conn.close()


def change_category_importance(category):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

    UPDATE Category
    SET category_importance = ?
    WHERE category_id = ?

    ''', [input("From 1 to 10, what is the new importance of the category? "), category[0]])
    conn.commit()
    c.close()
    conn.close()


def change_task_importance(task):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

    UPDATE Task
    SET task_importance = ?
    WHERE task_id = ?

    ''', [input("From 1 to 10, what is the new importance of the task to its category? "), task.id])
    conn.commit()
    c.close()
    conn.close()


def delete_category(category):
    if get_input("Are you sure you want to delete this category? (y/n)", str, allowed_values=('y', 'n')) != 'y':
        return
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''
    
    SELECT * FROM Task
    WHERE category_id = ?
    
    ''', [category[0]])
    if c.fetchone():
        print("There is still at least one task in this category.")
        print("Please reassign or delete all of these tasks before")
        print("attempting to delete this category.")
        return

    c.execute('''

        DELETE FROM Category
        WHERE category_id = ?

        ''', [category[0]])
    conn.commit()
    c.close()
    conn.close()


def delete_task(task):
    if get_input("Are you sure you want to delete this task? (y/n)", str, allowed_values=('y', 'n')) != 'y':
        return
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute('''

        DELETE FROM Task
        WHERE task_id = ?

        ''', [task.id])
    conn.commit()
    c.close()
    conn.close()


def manage_category(category):
    man_cat_menu = Menu.Menu()
    man_cat_menu.set_pre_menu_text(
        ("Managing category: " + category[1],
         "Importance of category: " + str(category[2]))
    )
    man_cat_menu.add_option("Change name of category", change_category_name, category)
    man_cat_menu.add_option("Change importance of category", change_category_importance, category)
    man_cat_menu.add_option("Delete category", delete_category, category)
    man_cat_menu.display("exit_on_choose")


def browse_categories(options):
    browse_categories_menu = Menu.Menu()
    categories = get_categories()
    for category in categories:
        browse_categories_menu.add_option(category[1] + "   " + str(category[2]), manage_category, category)
    browse_categories_menu.display(["exit_on_choose"])


def complete_task(task):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute('''

        UPDATE Task
        SET task_due_date = ?
        WHERE task_id = ?

        ''', [task.due_date + task.interval, task.id])
    conn.commit()
    c.close()
    conn.close()


def change_task_interval(task):
    print("Current task interval: " + str(task.interval))
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

    UPDATE Task
    SET task_interval = ?
    WHERE task_id = ?

    ''', [input("New interval of task: "), task.id])
    conn.commit()
    c.close()
    conn.close()


def put_off_task(task):
    year =get_input("Year to postpone until: ", int)
    month = get_input("Month to postpone until (1-12): ", int, greater_than=(0,), less_than=(13,))
    day = get_input("Day to postpone until: ", int, greater_than=(0,), less_than=(32,))
    hour = get_input("Hour to postpone until: ", int, greater_than=(-1,), less_than=(25,))
    minute = get_input("Minute to postpone until: ", int, greater_than=(-1,), less_than=(61,))
    postpone = datetime.date(int(year), int(month), int(day))
    postpone = postpone.toordinal()
    postpone += int(hour) / 24
    postpone += int(minute) / (24 * 60)
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''

    UPDATE Task
    SET task_postpone = ?
    WHERE task_id = ?

    ''', [postpone, task.id])
    conn.commit()
    c.close()
    conn.close()


def change_task_date(task):
    print("Current task due date: ")
    day = datetime.date.fromordinal(int(task.due_date))
    hour = int((task.due_date - int(task.due_date)) * 24)
    minute = int((((task.due_date - int(task.due_date)) * 24) - hour) * 60)
    print(str(day) + ", " + str(hour) + ":" + str(minute))
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    year_due = get_input("Year the task is due: ", int)
    month_due = get_input("Month the task is due (1-12): ", int, greater_than=(0,), less_than=(13,))
    day_due = get_input("Day the task is due: ", int, greater_than=(0,), less_than=(32,))
    hour_due = get_input("Hour the task is due: ", int, greater_than=(-1,), less_than=(25,))
    minute_due = get_input("Minute the task is due: ", int, greater_than=(-1,), less_than=(61,))
    date_due = datetime.date(int(year_due), int(month_due), int(day_due))
    date_due = date_due.toordinal()
    date_due += int(hour_due) / 24
    date_due += int(minute_due) / (24 * 60)
    c.execute('''

    UPDATE Task
    SET task_due_date = ?
    WHERE task_id = ?

    ''', [date_due, task.id])
    conn.commit()
    c.close()
    conn.close()


def manage_task(task):
    man_task_menu = Menu.Menu()
    man_task_menu.set_pre_menu_text(("Managing task: " + task.task_text,))
    man_task_menu.add_option("Change task text", change_task_text, task)
    man_task_menu.add_option("Change importance of task", change_task_importance, task)
    man_task_menu.add_option("Mark task complete", complete_task, task)
    man_task_menu.add_option("Change task interval", change_task_interval, task)
    man_task_menu.add_option("Delete task", delete_task, task)
    man_task_menu.add_option("Put off task", put_off_task, task)
    man_task_menu.add_option("Change date", change_task_date, task)
    man_task_menu.display("exit_on_choose")


def browse_tasks(tasks):
    browse_tasks_menu = Menu.Menu()
    if not tasks:
        tasks = get_tasks()
    for task in tasks:
        day = datetime.date.fromordinal(int(task.due_date))
        hour = int((task.due_date - int(task.due_date)) * 24)
        minute = int((((task.due_date - int(task.due_date)) * 24) - hour) * 60)
        browse_tasks_menu.add_option(task.task_text + ", due " + str(day) + ", " + str(hour) + ":" + str(minute),
                                     manage_task, task)
    browse_tasks_menu.display(["exit_on_choose"])


def filter_if_contains_quadrant1_tasks(task_list):
    max_imp = task_list[0].importance * task_list[0].category_importance
    min_imp = task_list[0].importance * task_list[0].category_importance
    max_due_date = task_list[0].due_date
    min_due_date = task_list[0].due_date
    for task in task_list:
        imp = task.importance * task.category_importance
        if imp > max_imp:
            max_imp = imp
        elif imp < min_imp:
            min_imp = imp
        if task.due_date > max_due_date:
            max_due_date = task.due_date
        elif task.due_date < min_due_date:
            min_due_date = task.due_date
    imp_midpoint = (max_imp + min_imp) / 2
    due_date_cutoff = datetime.datetime.now().toordinal() + 3
    due_date_midpoint = (max_due_date + datetime.datetime.now().toordinal()) / 2
    q1_tasks = []
    for task in task_list:
        imp = task.importance * task.category_importance
        if imp >= imp_midpoint and task.due_date < due_date_midpoint and task.due_date < due_date_cutoff:
            q1_tasks.append(task)
    if len(q1_tasks) > 8:
        q1_tasks = filter_if_contains_quadrant1_tasks(q1_tasks)
    if q1_tasks:
        print("True")
        return q1_tasks
    print("False")
    return task_list


def filter_is_tasks_overdue(task_list):
    overdue_tasks = []
    for task in task_list:
        if task.due_date < datetime.datetime.now().toordinal():
            overdue_tasks.append(task)
    if overdue_tasks:
        print("True")
        return overdue_tasks
    print("False")
    return task_list


def view_next_tasks(options):
    global user_id
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    tasks = get_tasks()
    valid_tasks = []
    now = datetime.datetime.now()
    now_ord = now.toordinal()
    now_ord += now.hour / 24
    now_ord += now.minute / (24 * 60)
    for task in tasks:
        if (task.due_date <= now_ord or (task.due_date > now_ord and task.allow_early_completion == 'y')) \
                and task.postpone <= now_ord:
            # reset_postpone(task)
            valid_tasks.append(task)
    min_imp = 10
    max_imp = 0
    min_urg = tasks[0].due_date
    max_urg = tasks[0].due_date
    top_5 = []
    top_5_priorities = []
    for valid_task in valid_tasks:
        imp = int(valid_task.category_importance) * int(valid_task.importance) / 10
        if imp > max_imp:
            max_imp = imp
        elif imp < min_imp:
            min_imp = imp
        if valid_task.due_date > max_urg:
            max_urg = valid_task.due_date
        if valid_task.due_date < min_urg:
            min_urg = valid_task.due_date
    x = []
    y = []
    z = []
    valid_tasks = filter_if_contains_quadrant1_tasks(valid_tasks)
    print(" ")
    valid_tasks = filter_is_tasks_overdue(valid_tasks)
    for valid_task in valid_tasks:
        imp = int(valid_task.category_importance) * int(valid_task.importance) / 10
        x.append(imp)
        y.append(valid_task.due_date)
        priority = (imp - min_imp + 0.01) ** 1.1 + (max_urg - valid_task.due_date + 0.01)
        z.append(priority)
        added = False
        for i in range(len(top_5_priorities)):
            if not top_5_priorities:
                top_5.append(valid_task)
                top_5_priorities.append(priority)
                added = True
                break
            if priority > top_5_priorities[i]:
                top_5.insert(i, valid_task)
                top_5_priorities.insert(i, priority)
                added = True
                break
        if not added:
            top_5.append(valid_task)
            top_5_priorities.append(priority)
    # print(top_5)
    # print(top_5_priorities)

    # x = []
    # y = []
    # z = []
    # for i in range(100):
    #     for j in range(100):
    #         x.append(i)
    #         y.append(j)
    # for index, element in enumerate(x):
    #     priority = (x[index] + 0.01) ** 1.1 + (max(y) - y[index] + 0.01)
    #     z.append(priority)
    #
    #
    # cmap = matplotlib.cm.get_cmap('viridis')
    # normalize = matplotlib.colors.Normalize(vmin=min(z), vmax=max(z))
    # colors = [cmap(normalize(value)) for value in z]
    #
    # fig, ax = plt.subplots(figsize=(10, 10))
    # ax.scatter(x, y, color=colors)
    #
    # # Optionally add a colorbar
    # cax, _ = matplotlib.colorbar.make_axes(ax)
    # cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)
    # plt.show()

    browse_tasks(top_5[:8])
    c.close()
    conn.close()


def main():
    db = Path("data.db")
    if not db.is_file():
        first_run()

    categories_menu = Menu.Menu()
    categories_menu.add_option("Add a category", add_category, None)
    categories_menu.add_option("Browse categories", browse_categories, None)

    tasks_menu = Menu.Menu()
    tasks_menu.add_option("View next tasks", view_next_tasks, None)
    tasks_menu.add_option("Browse tasks", browse_tasks, None)
    tasks_menu.add_option("Add a task", add_task, None)

    logged_in_menu = Menu.Menu()
    logged_in_menu.add_option("Tasks", tasks_menu.display, None)
    logged_in_menu.add_option("Categories", categories_menu.display, None)

    main_menu = Menu.Menu()
    main_menu.add_option("Log in", try_log_in, [logged_in_menu])
    main_menu.add_option("Create user", create_user, None)

    main_menu.display(None)


main()
