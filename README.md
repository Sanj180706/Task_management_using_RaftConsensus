# Task Management using Raft Consensus

Raft is a consensus algorithm designed for managing a replicated log in a distributed system. It ensures that all nodes in a cluster agree on the same sequence of entries in the log, even in the presence of failures. Raft is based on a leader-follower model, where one node serves as the leader and coordinates the replication process, while the other nodes act as followers and replicate the leader's log.

In a Raft-based system using MySQL, each node in the cluster would have its own MySQL database instance to store the replicated log. The leader would receive client requests, append entries to its log, and replicate them to followers. Followers would apply these entries to their logs and respond to clients with the results. If the leader fails, a new leader is elected through an interactive process among the nodes, ensuring the system's availability and consistency.

| Name                                           | SRN           | Section |
| :--------------------------------------------- | :------------ | :-----: |
| [Sanjay Sunil](https://github.com/Sanj180706)  | PES1UG21CS535 |    I    |
| [Sarang Kumar](https://github.com/SarangKumar) | PES1UG21CS537 |    I    |
| Vasanth Seemakurthy                            | PES1UG21CS437 |    I    |
| [Sai Harshith Narra](https://github.com/SaiHarshithN2003)| PES1UG21CS513 |    I    |
