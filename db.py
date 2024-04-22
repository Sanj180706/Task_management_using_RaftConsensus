import mysql.connector

class TaskManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        self.mysqldb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.mycursor = self.mysqldb.cursor()

    def create_task_table(self):
        self.mycursor.execute("""
        
                              
        CREATE TABLE IF NOT EXISTS tasks (
            taskid INT AUTO_INCREMENT PRIMARY KEY,
            taskname VARCHAR(255) NOT NULL,
            taskstatus VARCHAR(50),
            taskdur INT
        )
        """)
        self.mysqldb.commit()

    def add_task(self, taskname, taskstatus, taskdur):
        sql = "INSERT INTO tasks (taskname, taskstatus, taskdur) VALUES (%s, %s, %s)"
        val = (taskname, taskstatus, taskdur)
        self.mycursor.execute(sql, val)
        self.mysqldb.commit()
        return self.mycursor.lastrowid

    def update_task(self, taskid, taskname=None, taskstatus=None, taskdur=None):
        updates = []
        if taskname:
            updates.append(f"taskname = '{taskname}'")
        if taskstatus:
            updates.append(f"taskstatus = '{taskstatus}'")
        if taskdur:
            updates.append(f"taskdur = {taskdur}")
        if not updates:
            return False
        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE taskid = {taskid}"
        self.mycursor.execute(sql)
        self.mysqldb.commit()
        return True

    def get_task(self, taskid):
        sql = f"SELECT * FROM tasks WHERE taskid = {taskid}"
        self.mycursor.execute(sql)
        return self.mycursor.fetchone()

    def delete_task(self, taskid):
        sql = f"DELETE FROM tasks WHERE taskid = {taskid}"
        self.mycursor.execute(sql)
        self.mysqldb.commit()

    def close_connection(self):
        self.mysqldb.close()

# Usage example
if __name__ == "__main__":
    tm = TaskManager(host="localhost", user="root", password="password", database="task_management_cs535_cs537_cs547_cs513")
    tm.create_task_table()
    
    taskid = tm.add_task("Task 1", "Pending", 2)
    print("Task added with ID:", taskid)
    
    print("Task details:", tm.get_task(taskid))
    
    tm.update_task(taskid, taskdur=5)
    print("Task details after update:", tm.get_task(taskid))
    
    
    # tm.delete_task(taskid)
    # print("Task deleted")
    
    tm.close_connection()
