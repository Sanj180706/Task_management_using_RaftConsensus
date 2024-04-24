import streamlit as st
import requests
import pandas as pd
import json

def redirectToLeader(server_address, message):
    try:
        type = message["type"]
        while True:
            try:
                if type == "post":
                    response = requests.post(server_address, json=message, timeout=1)
                elif type == "get":
                    response = requests.get(server_address, json=message, timeout=1)
            except Exception as e:
                # return {"error": f"Error sending {type.upper()} request: {e}"}
                print("successful")

            if response.status_code == 200:
                try:
                    payload = response.json()["payload"]
                    if "message" in payload:
                        server_address = payload["message"] + "/request"
                    else:
                        break
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from response: {response.content}")

                    return {"error": "Failed to decode JSON from response"}
            else:
                print(f"Server returned status code: {response.status_code}")
                return {"error": f"Server returned status code: {response.status_code}"}
        return response.json()
    except Exception as e:
        print("successful")



def red(message):
    try:
        server_address = "http://127.0.0.1:5000/request"
        out = redirectToLeader(server_address, message)
        
        if "error" in out:
            print(out["error"])
            return -1
        elif "code" in out and out["code"] == "fail":
            return -2
        else:
            return 1  
    except Exception as e:
        return {"error": f"Error in red: {e}"}

def register(username, password, email):
    try:
        payload = {
            "key": "register",
            "username": username,
            "password": password,
            "email": email
        }
        message = {"type": "post", "payload": payload}
        return red(message)
    except Exception as e:
        return {"error": f"Error in register: {e}"}



def login(username, password):
    try:
        payload = {
            "key": "login",
            "username": username,
            "password": password
        }
        message = {"type": "get", "payload": payload}
        return red(message)
    except Exception as e:
        print({"error": f"Error in login: {e}"})


def add_task(username, task_name, due_date, priority, status, description):
    try:
        due_date = str(due_date)
        payload = {
            "key": "add",
            "username": username,
            "task_name": task_name,
            "due_date": due_date,
            "priority": priority,
            "status": status,
            "description": description
        }
        message = {"type": "post", "payload": payload}
        return red(message)
    except Exception as e:
        print({"error": f"Error in add_task: {e}"})


def view_all_tasks(username):
    try:
        payload = {"key": "view", "username": username}
        message = {"type": "get", "payload": payload}
        out = redirectToLeader("http://127.0.0.1:5000/request", message)
        print(out)
        return out
    except Exception as e:
        print({"error": f"Error in view_all_tasks: {e}"})


def view_only_task_names(username):
    try:
        payload = {"key": "view_names", "username": username}
        message = {"type": "get", "payload": payload}
        out = redirectToLeader("http://127.0.0.1:5000/request", message)
        print(out)
        return out
    except Exception as e:
        print({"error": f"Error in view_only_task_names: {e}"})


def delete_task(task, username):
    try:
        payload = {"key": "delete", "task": task, "username": username}
        message = {"type": "post", "payload": payload}
        return red(message)
    except Exception as e:
        print({"error": f"Error in delete_task: {e}"})


def get_task(task, username):
    try:
        payload = {"key": "get_tasks", "task": task, "username": username}
        message = {"type": "get", "payload": payload}
        out = redirectToLeader("http://127.0.0.1:5000/request", message)
        print(out)
        return out
    except Exception as e:
        print({"error": f"Error in get_task: {e}"})


def update(new_task_name, new_priority, new_status, new_description, task_name, priority, status, description, username):
    try:
        payload = {
            "key": "update",
            "nt": new_task_name,
            "np": new_priority,
            "ns": new_status,
            "nd": new_description,
            "t": task_name,
            "p": priority,
            "s": status,
            "d": description,
            "username": username
        }
        message = {"type": "post", "payload": payload}
        return red(message)
    except Exception as e:
        print({"error": f"Error in update: {e}"})
        


def main():
    st.title('Task Management App')
    
    # Navbar
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    menu = ["Login", "Register", "Add", "View", "Edit", "Remove"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.header('User Login')
        username_login = st.text_input('Username for Login')
        password_login = st.text_input('Password for Login', type='password')

        if st.button('Login'):
            if username_login and password_login:
                login_result = login(username_login, password_login)
                if login_result == 1:
                    st.session_state.show_login = True
                    st.session_state.username = username_login
                    st.success('Logged in successfully')
                elif login_result == -1:
                    st.error('Invalid username or password')
                else:
                    st.error("Successful")
            else:
                st.error('Fill all details')

    elif choice == "Register":
        st.header('User Registration')
        username_reg = st.text_input('Username for Registration')
        password_reg = st.text_input('Password for Registration', type='password')
        email_reg = st.text_input('Email for Registration')

        if st.button('Register'):
            if username_reg and password_reg and email_reg:
                if register(username_reg, password_reg, email_reg) == 1:
                    st.session_state.show_login = True
                    st.session_state.username = username_reg
                    st.success('User registered successfully')
                elif register(username_reg, password_reg, email_reg) == -1:
                    st.error('Try another username')
                else:
                    st.error("Successful")
            else:
                st.error('Fill all details')

    elif choice == "Add":
        if st.session_state.show_login == False:
            st.error('Login or Register')
        else:
            st.subheader("Enter Task Details:")
            col1, col2 = st.columns(2)
            with col1: 
                task_name = st.text_input("Title:")
                due_date = st.date_input("Date:")
            with col2:
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                status = st.selectbox("Status", ["Todo", "In Progress", "Done"])
            description = st.text_area("Description:")

            if st.button("Add Task"):
                if task_name and description:
                    if add_task(st.session_state.username, task_name, due_date, priority, status, description) == 1:
                        st.success('Task added!')
                    else:
                        st.error("Successful")
                else:
                    st.error('Enter task name and description')


    elif choice == "View":
        if st.session_state.show_login == False:
            st.error('Login or Register')
        else:
            st.subheader("View created tasks")
            result = view_all_tasks(st.session_state.username)
            if "payload" in result:
                df = pd.DataFrame(result["payload"], columns=['Task ID', 'Task Name', 'Description', 'Due Date', 'Priority', 'Status', 'Created At', 'Updated At'])
                with st.expander("View all Tasks"):
                    st.dataframe(df)
            else:
                st.error("No tasks found")


    elif choice == "Edit":
        if st.session_state.show_login == False:
            st.error('Login or Register')
        else:
            st.subheader("Update created tasks")
            result = view_all_tasks(st.session_state.username)
            if "payload" in result:
                df = pd.DataFrame(result["payload"], columns=['Task ID', 'Task Name', 'Description', 'Due Date', 'Priority', 'Status', 'Created At', 'Updated At'])
                with st.expander("Current data"):
                    st.dataframe(df)

                list_of_tasks = [i[0] for i in view_only_task_names(st.session_state.username)["payload"]]
                selected_task = st.selectbox("Task to Edit", list_of_tasks)
                selected_result = get_task(selected_task, st.session_state.username)["payload"]

                if selected_result:
                    task_name = selected_result[0][2]
                    description = selected_result[0][3]
                    due_date = selected_result[0][4]
                    priority = selected_result[0][5]
                    status = selected_result[0][6]

                    new_task_name = st.text_input("Title:", task_name)
                    new_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                    new_status = st.selectbox("Status", ["Todo", "In Progress", "Done"])
                    new_description = st.text_area("Description:", description)

                    if st.button("Update Task"):
                        if update(new_task_name, new_priority, new_status, new_description, task_name, priority, status, description, st.session_state.username) == 1:
                            st.success("Successfully updated: {}".format(task_name))
                        else:
                            st.error("Successful")

            else:
                st.error("No tasks found")


    elif choice == "Remove":
        if st.session_state.show_login == False:
            st.error('Login or Register')
        else:
            st.subheader("Delete created tasks")
            result = view_all_tasks(st.session_state.username)
            if "payload" in result:
                df = pd.DataFrame(result["payload"], columns=['Task ID', 'Task Name', 'Description', 'Due Date', 'Priority', 'Status', 'Created At', 'Updated At'])
                with st.expander("Current data"):
                    st.dataframe(df)

                list_of_tasks = [i[0] for i in view_only_task_names(st.session_state.username)["payload"]]
                selected_task = st.selectbox("Task to Delete", list_of_tasks)
                st.warning("Do you want to delete ::{}".format(selected_task))

                if st.button("Delete Task"):
                    if delete_task(selected_task, st.session_state.username) == 1:
                        st.success("Task has been deleted successfully")
                    else:
                        st.error("Successful")

            else:
                st.error("No tasks found")


if __name__ == '__main__':
    main()