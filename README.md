# **Task Management using Raft Consensus**

## Initilation 

### Creating virtual environment

```bash
python -m venv venv
venv/Scripts/activate #only for win
```

### Installing modules

```bash
pip install -r requirements.txt
```

### DB init



In `node.py` make changes to this line according to your configuration.
```bash
self.mydb = mysql.connector.connect(host="localhost", user="root",password="password123", database="")
```

Make sure that the database is already created with the name `task`. Also the tables,`users` and `tasks`, also need to be made before running the code 

- Creating db
```bash
drop database task;
create database task;
use task;
```

- Creating table
```bash
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    priority ENUM('Low', 'Medium', 'High') NOT NULL,
    status ENUM('Todo', 'In Progress', 'Done') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

```

### To run servers

> If you get any error then use only 3 terminals

- Terminal 1
```bash
venv/Scripts/activate
python server.py 0 ip_list.txt
```

- Terminal 2
```bash
venv/Scripts/activate
python server.py 1 ip_list.txt
```

- Terminal 3
```bash
venv/Scripts/activate
python server.py 2 ip_list.txt
```

- Terminal 4
```bash
venv/Scripts/activate
python server.py 3 ip_list.txt
```

- Terminal 5
```bash
venv/Scripts/activate
python server.py 4 ip_list.txt
```

- Terminal 6
```bash
venv/Scripts/activate
# streamlit run app.py
streamlit run app.py --client.showErrorDetails=false
```