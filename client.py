import sys, requests


def redirectToLeader(server_address, message):
    type = message["type"]
    # looping until someone tells he is the leader
    while True:
        # switching between "get" and "put"
        if type == "get":
            try:
                response = requests.get(server_address,
                                        json=message,
                                        timeout=1)
            except Exception as e:
                return e
        else:
            try:
                response = requests.put(server_address,
                                        json=message,
                                        timeout=1)
            except Exception as e:
                return e

        # if valid response and an address in the "message" section in reply
        # redirect server_address to the potential leader
        if response.status_code == 200 and "payload" in response.json():
            payload = response.json()["payload"]
            if "message" in payload:
                server_address = payload["message"] + "/request"
            else:
                break
        else:
            break
    # if type == "get":
    return response.json()
    # else:
    #     return response


# client put request
def put(addr, taskid, taskname, taskdur, taskstatus):
    server_address = addr + "/request"
    '''payload = {'key': key, 'value': value}
    message = {"type": "put", "payload": payload}'''
    query = ("INSERT INTO TASKS (taskid, taskname, taskdur, taskstatus) VALUES (%s, %s, %s, %s)",(taskid,taskname,taskdur,taskstatus))
    #cursor.execute(query)

    # redirecting till we find the leader, in case of request during election
    print(redirectToLeader(server_address, message))


# client get request
def get(addr, query):
    server_address = addr + "/request"
    '''payload = {'key': key}
    message = {"type": "get", "payload": payload}'''
    # redirecting till we find the leader, in case of request during election
    print(redirectToLeader(server_address, query))


if __name__ == "__main__":
    while True:
        inp = input("Choose from the options: \
1) Create a task\
2) Update a task\
3) Show all tasks\
4) Delete a task")
        if inp == '1':
            taskid = input("Enter task ID: ")
            taskname = input("Enter task name: ")
            taskdur = int(input("Enter task duration in minutes: "))
            taskstatus = input("Enter the status of the task: ")
            addr = sys.argv[1]
            put(addr, taskid, taskname, taskdur, taskstatus)
        elif inp == '3':
            addr = sys.argv[1]
            query = "select * from tasks;"
            get(addr, query)
        else:
            break
        	
    '''if len(sys.argv) == 3:
        # addr, key
        # get
        addr = sys.argv[1]
        key = sys.argv[2]
        get(addr, key)
    elif len(sys.argv) == 4:
        # addr, key value
        # put
        addr = sys.argv[1]
        key = sys.argv[2]
        val = sys.argv[3]
        put(addr, key, val)
    else:
        print("PUT usage: python3 client.py address 'key' 'value'")
        print("GET usage: python3 client.py address 'key'")
        print("Format: address: http://ip:port")'''