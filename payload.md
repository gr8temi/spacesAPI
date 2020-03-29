# Endpoints data

### Creating Space data
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
### Login User

```
Route = "api/v1/auth/login/"

data = {
    username = string,
    password = string,
}
```

### Create Agent

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

### create agent from a customer

```
Route = "api/v1/auth/agents/signup/"

data = {
    email=string,
    business_name:string,
    office_address:string
}
```

### Get all Agents
```
Route = Route = "api/v1/agents/"
```

### Get/Delete an Agent
```
Route = Route = "api/v1/auth/agent/user_id/"
```

### Update an Agent
```

Route = Route = "api/v1/auth/agent/user_id/"

data = {
    **fields to be updated
}
```

### Create Customer

```
Route = "api/v1/auth/customers/signup/"

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

### Get all Customers
```
Route = Route = "api/v1/customers/"
```

### Get/Delete an Customer
```
Route = Route = "api/v1/auth/customer/user_id/"
```

### Update an Customer
```

Route = Route = "api/v1/auth/customer/user_id/"

data = {
    **fields to be updated
}
```