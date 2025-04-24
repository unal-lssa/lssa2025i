# E-commerce

## Components: 

 - BD SQL
 - REST components (Orders, User Data) (Replica)
 - GraphQL (products)
 - Load Balancer
 - API Gateway
 - MQTP
 - Front Ends


 ## Domain

(Authentication, User Info) -> SQL, REST, API GAteway
 User -> id 
        name
        isCustomer
        isSeller

CRUD -> REST, SQL
 Product -> id
             name
             price
             type
             user_id


CRUD -> REST, SQL  
Inventory -> product_id
             Quantity
             Region


GraphQL [Read, Update] -> SQL
Order -> id
         customer_id
         status
        

order_detail -> order_id
                prduct_id
                quantity
                total_price


Read/MQTP -> SQL, REST
Payments -> payment_id
            order_id
            payment_method
            total_payment
            transaction_id
            status