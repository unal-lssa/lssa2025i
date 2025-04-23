# TODO: Consolidar la documentacion del la primera entrega del proyecto

# Diagrama inicial de componentes:
```mermaid
graph TD
    efact_lb1["efact_lb1 (LOAD_BALANCER)"]
    efact_lb2["efact_lb2 (LOAD_BALANCER)"]
    admin_fe["admin_fe (FRONTEND)"]
    report_fe["report_fe (FRONTEND)"]
    user_fe["user_fe (FRONTEND)"]
    efact_ag["efact_ag (API_GATEWAY)"]
    efact_lb3["efact_lb3 (LOAD_BALANCER)"]
    efact_lb4["efact_lb4 (LOAD_BALANCER)"]
    efact_lb5["efact_lb5 (LOAD_BALANCER)"]
    efact_lb6["efact_lb6 (LOAD_BALANCER)"]
    perna_be["perna_be (BACKEND)"]
    perju_be["perju_be (BACKEND)"]
    busre_be["busre_be (BACKEND)"]
    proc_be["proc_be (BACKEND)"]
    perna_db["perna_db (DATABASE)"]
    perju_db["perju_db (DATABASE)"]
    busre_db["busre_db (DATABASE)"]
    proc_db["proc_db (DATABASE)"]

    efact_lb1 -->|lb_conn| report_fe
    efact_lb2 -->|lb_conn| user_fe

    admin_fe -->|http| efact_ag
    report_fe -->|http| efact_ag
    user_fe -->|http| efact_ag

    efact_ag -->|http| efact_lb3
    efact_ag -->|http| efact_lb4
    efact_ag -->|http| efact_lb5
    efact_ag -->|http| efact_lb6

    efact_lb3 -->|lb_conn| perna_be
    efact_lb4 -->|lb_conn| perju_be
    efact_lb5 -->|lb_conn| busre_be
    efact_lb6 -->|lb_conn| proc_be

    perna_be -->|db_conn| perna_db
    perju_be -->|db_conn| perju_db
    busre_be -->|db_conn| busre_db
    proc_be -->|db_conn| proc_db
```
