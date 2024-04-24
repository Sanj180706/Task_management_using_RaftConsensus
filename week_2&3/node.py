import threading
import time
import utils
from utils import cfg
import mysql.connector

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2

class Node():
    def __init__(self, fellow, my_ip):
        try:
            self.addr = my_ip
            self.fellow = fellow
            self.lock = threading.Lock()
            self.mydb = mysql.connector.connect(host="localhost", user="root", password="password", database="task")
            self.log = []
            self.staged = None
            self.term = 0
            self.status = FOLLOWER
            self.majority = (len(self.fellow) // 2) + 1
            self.voteCount = 0
            self.commitIdx = 0
            self.timeout_thread = None
            self.init_timeout()
        except Exception as e:
            print(f"Error initializing Node: {e}")

    def incrementVote(self):
        try:
            self.voteCount += 1
            if self.voteCount >= self.majority:
                print(f"{self.addr} becomes the leader of term {self.term}")
                self.status = LEADER
                self.startHeartBeat()
        except Exception as e:
            print(f"Error incrementing vote: {e}")

    def startElection(self):
        try:
            self.term += 1
            self.voteCount = 1
            self.status = CANDIDATE
            self.init_timeout()
            self.incrementVote()
            self.send_vote_req()
        except Exception as e:
            print(f"Error starting election: {e}")

    def send_vote_req(self):
        try:
            for voter in self.fellow:
                threading.Thread(target=self.ask_for_vote,
                                args=(voter, self.term)).start()
        except Exception as e:
            print(f"Error sending vote request: {e}")
            

    def ask_for_vote(self, voter, term):
        try:
            message = {
                "term": term,
                "commitIdx": self.commitIdx,
                "staged": self.staged
            }
            route = "vote_req"
            while self.status == CANDIDATE and self.term == term:
                reply = utils.send(voter, route, message)
                if reply:
                    choice = reply.json()["choice"]
                    if choice and self.status == CANDIDATE:
                        self.incrementVote()
                    elif not choice:
                        term = reply.json()["term"]
                        if term > self.term:
                            self.term = term
                            self.status = FOLLOWER
                    break
        except Exception as e:
            print(f"Error asking for vote: {e}")
            

    def decide_vote(self, term, commitIdx, staged):
        try:
            if self.term < term and self.commitIdx <= commitIdx and (
                    staged or (self.staged == staged)):
                self.reset_timeout()
                self.term = term
                return True, self.term
            else:
                return False, self.term
        except Exception as e:
            print(f"Error deciding vote: {e}")
        
    def startHeartBeat(self):
        try:
            print("Starting HEARTBEAT")
            if self.staged:
                self.handle_put(self.staged)

            for each in self.fellow:
                t = threading.Thread(target=self.send_heartbeat, args=(each, ))
                t.start()
        except Exception as e:
            print(f"Error starting heartbeat: {e}")

    def update_follower_commitIdx(self, follower):
        try:
            route = "heartbeat"
            first_message = {"term": self.term, "addr": self.addr}
            second_message = {
                "term": self.term,
                "addr": self.addr,
                "action": "commit",
                "payload": self.log[-1]
            }
            reply = utils.send(follower, route, first_message)
            if reply and reply.json()["commitIdx"] < self.commitIdx:
                reply = utils.send(follower, route, second_message)
        except Exception as e:
            print(f"Error updating follower commitIdx: {e}")

    def send_heartbeat(self, follower):
        try:
            if self.log:
                self.update_follower_commitIdx(follower)

            route = "heartbeat"
            message = {"term": self.term, "addr": self.addr}
            while self.status == LEADER:
                start = time.time()
                reply = utils.send(follower, route, message)
                if reply:
                    self.heartbeat_reply_handler(reply.json()["term"],
                                                reply.json()["commitIdx"])
                delta = time.time() - start
                time.sleep((cfg.HB_TIME - delta) / 1000)
        except Exception as e:
            print(f"Error sending heartbeat: {e}")

    def heartbeat_reply_handler(self, term, commitIdx):
        try:
            if term > self.term:
                self.term = term
                self.status = FOLLOWER
                self.init_timeout()
        except Exception as e:
            print(f"Error handling heartbeat reply: {e}")

    def reset_timeout(self):
        try:
            self.election_time = time.time() + utils.random_timeout()
        except Exception as e:
            print(f"Error resetting timeout: {e}")

    def heartbeat_follower(self, msg):
        try:
            term = msg["term"]
            if self.term <= term:
                self.leader = msg["addr"]
                self.reset_timeout()
                if self.status == CANDIDATE:
                    self.status = FOLLOWER
                elif self.status == LEADER:
                    self.status = FOLLOWER
                    self.init_timeout()

                if self.term < term:
                    self.term = term

                if "action" in msg:
                    print("received action", msg)
                    action = msg["action"]
                    if action == "log":
                        payload = msg["payload"]
                        self.staged = payload
                    elif "commitIdx" in msg and self.commitIdx <= msg["commitIdx"]:
                        if not self.staged:
                            self.staged = msg["payload"]
                        # self.commit()

            return self.term, self.commitIdx
        except Exception as e:
            print(f"Error handling heartbeat follower: {e}")


    def init_timeout(self):
        try:
            self.reset_timeout()
            if self.timeout_thread and self.timeout_thread.is_alive():
                return
            self.timeout_thread = threading.Thread(target=self.timeout_loop)
            self.timeout_thread.start()
        except Exception as e:
            print(f"Error initializing timeout: {e}")

    def timeout_loop(self):
        try:
            while self.status != LEADER:
                delta = self.election_time - time.time()
                if delta < 0:
                    self.startElection()
                else:
                    time.sleep(delta)
        except Exception as e:
            print(f"Error in timeout loop: {e}")

    def handle_get(self, payload):
        try:
            print("getting", payload)
            key = payload["key"]
            if key == "login":
                username = payload["username"]
                password = payload["password"]
                    
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT COUNT(*) FROM users WHERE username = %s and password_hash = %s"
                    cursor.execute(sql_check, (username,password,))
                    result = cursor.fetchone()
                    if result[0] == 0:
                        return -1
                    else:
                        return "User Exists"
                    
            if key == "view":
                username = payload["username"]
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "SELECT task_id, title, description, due_date, priority, status, created_at, updated_at FROM tasks WHERE user_id = %s"
                    cursor.execute(sql, (result[0],))
                    data = cursor.fetchall()
                    print(data)
                    return data
                
            if key == "view_names":
                username = payload["username"]
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "SELECT title FROM tasks WHERE user_id = %s"
                    cursor.execute(sql, (result[0],))
                    data = cursor.fetchall()
                    print(data)
                    return data
                
            if key == "get_tasks":
                username = payload["username"]
                task = payload["task"]
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "SELECT * FROM tasks WHERE title = %s AND user_id = %s"
                    cursor.execute(sql, (task, result[0],))
                    data = cursor.fetchall()
                    print(data)
                    return data
            return -1
        except Exception as e:
            print(f"Error handling get: {e}")
            return -1

    def spread_update(self, message, confirmations=None, lock=None):
        try:
            for i, each in enumerate(self.fellow):
                r = utils.send(each, "heartbeat", message)
                if r and confirmations:
                    confirmations[i] = True
            if lock:
                lock.release()
        except Exception as e:
            print(f"Error spreading update: {e}")

    def handle_put(self, payload):
        try:
            print("putting", payload)

            self.lock.acquire()
            self.staged = payload
            waited = 0
            log_message = {
                "term": self.term,
                "addr": self.addr,
                "payload": payload,
                "action": "log",
                "commitIdx": self.commitIdx
            }

            log_confirmations = [False] * len(self.fellow)
            threading.Thread(target=self.spread_update,
                            args=(log_message, log_confirmations)).start()
            while sum(log_confirmations) + 1 < self.majority:
                waited += 0.0005
                time.sleep(0.0005)
                if waited > cfg.MAX_LOG_WAIT / 1000:
                    print(f"waited {cfg.MAX_LOG_WAIT} ms, update rejected:")
                    self.lock.release()
                    return False

            commit_message = {
                "term": self.term,
                "addr": self.addr,
                "payload": payload,
                "action": "commit",
                "commitIdx": self.commitIdx
            }
            r = self.commit()
            threading.Thread(target=self.spread_update,
                            args=(commit_message, None, self.lock)).start()
            print("majority reached, replied to client, sending message to commit")
            return r
        except Exception as e:
            print(f"Error handling put: {e}")

    def commit(self):
        try:
            self.commitIdx += 1
            self.log.append(self.staged)
            key = self.staged["key"]

            if key == "register":
                username = self.staged["username"]
                password = self.staged["password"]
                email = self.staged["email"]
                    
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT COUNT(*) FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    if result[0] > 0:
                        return -1
                    sql = "INSERT IGNORE INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (username, password, email))

                self.mydb.commit()

            if key == "add":
                username = self.staged["username"]
                task_name = self.staged["task_name"]
                due_date = self.staged["due_date"]
                priority = self.staged["priority"]
                status = self.staged["status"]
                description = self.staged["description"]
                    
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "INSERT IGNORE INTO tasks (user_id, title, description, due_date, priority, status) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (result[0], task_name, description, due_date, priority, status))
                self.mydb.commit()
            
            if key == "delete":
                username = self.staged["username"]
                task_name = self.staged["task"]
                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "DELETE FROM tasks WHERE title = %s and user_id = %s"
                    cursor.execute(sql, (task_name, result[0],))
                self.mydb.commit()
            
            if key == "update":
                username = self.staged["username"]
                t= self.staged["t"]
                p = self.staged["p"]
                s = self.staged["s"]
                d = self.staged["d"]
                nt= self.staged["nt"]
                np = self.staged["np"]
                ns = self.staged["ns"]
                nd = self.staged["nd"]

                with self.mydb.cursor() as cursor:
                    sql_check = "SELECT user_id FROM users WHERE username = %s"
                    cursor.execute(sql_check, (username,))
                    result = cursor.fetchone()
                    sql = "UPDATE tasks SET title = %s, description = %s, priority = %s, status = %s WHERE user_id = %s AND title = %s AND description = %s AND priority = %s AND status = %s"
                    cursor.execute(sql, (nt, nd, np, ns, result[0], t, d, p, s))
                self.mydb.commit()
                
            self.staged = None
            return 1
        except Exception as e:
            print(f"Error committing: {e}")
            return -1
