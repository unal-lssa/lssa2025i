# E-commerce

## Components: 

 - BD SQL -Postgres 
 - REST components (Orders, User Data) (Replica) - FastAPI
 - Load Balancer - Nginx (Alejandro)
 - API Gateway - Nginx/Header (Alejandro)
 - MQTP - RabbitMQ :=> delay 30s (Yosman)
 - Front Ends - HTML + Bootstrap Fetch (Nginx) (Diego)


 ## Domain

(Authentication, User Info) -> SQL, REST, API GAteway
 User -> id (Juan David)
        name
        isCustomer
        isSeller

CRUD -> REST, SQL
 Product -> id (Alejandro)
             name
             price
             type
             user_id


CRUD -> REST, SQL  
Inventory -> product_id (Diego)
             Quantity
             Region


 [Read, Update] -> SQL
Order -> id (Sergio)
         customer_id
         status
        

order_detail -> order_id (Sergio)
                product_id
                quantity
                total_price


Read/MQTP -> SQL, REST
Payments -> payment_id (Yosman)
            order_id
            payment_method
            total_payment
            transaction_id
            status