# Endpoints data

### Creating Space data POST
```
Route = "api/v1/spaces/"

data = {
number_of_bookings:integer,
agent: agent's UUID,
description: string,
space_category: category's UUID,
price:string,
location:string,
name:string
}
```


### Get all spaces
```
Route = "v1/all-spaces/
```

### Login User POST


```
Route = "api/v1/auth/login/"

data = {
    username = string,
    password = string,
}
```

### Create Agent POST

```
Route = "api/v1/auth/agents/signup/"

data = {
    username: string,
    email:string,
    phone_number:string,
    name:string,
    business_name:string,
    office_address: string,
    password:string
}
```

### create agent from a user POST

```
Route = "api/v1/auth/agents/signup/"

data = {
    email=string,
    business_name:string,
    office_address:string
}
```

### Get all Agents GET
```
Route = Route = "api/v1/agents/"
```

### Get/Delete an Agent
```
Route = Route = "api/v1/auth/agent/user_id/"
```

### Update an Agent PUT
```

Route = Route = "api/v1/auth/agent/user_id/"

data = {
    **fields to be updated
}
```

### Create Customer POST

```
Route = "api/v1/auth/customers/signup/"

data = {
    username: string,
    email:string,
    phone_number:string,
    name:string,
    password:string
}
```

### Get all Customers GET
```
Route = Route = "api/v1/customers/"
```

### Get/Delete a Customer
```
Route = Route = "api/v1/auth/customer/user_id/"
```

### Update an Customer PUT
```

Route = Route = "api/v1/auth/customer/user_id/"

data = {
    **fields to be updated
}
```
#### Verify Email POST
````

Route = Route = "api/v1/auth/verify-email/"

data = {
    token: token sent to email(string)
}
````
#### Forgot Password POST
````

Route = Route = "api/v1/auth/forgot-password/"

data = {
    username: agent or customer username
}
````
#### Reset Password POST
````

Route = Route = "api/v1/auth/reset-password/"

data = {
    token: string,
    password: new password
}
````
#### Booking POST
````
Route = "api/v1/booking/

````
data = {
    usage_start_date: Date field,
    usage_end_date: date field,
    transaction_code: code generated on payment
    order_type: string
    space: string

}


#### Single Space GET

```
Route = "v1/space/space_id/"

append UUID to url
```

````
#### Reservation (method = POST)
````
Route = Route = "api/v1/reservation/"
````
data = {
    usage_start_date: Date field,
    usage_end_date: date field,
    transaction_code: string
    order_type: string
    space: string
}

````
#### Complete Order (method = PUT)
````
Route = Route = "api/v1/reservation/"
````
data = {
    order_code: string,
    transaction_code: string
}
