# API Documentation

- ## <span style="color:orange">**POST**</span> Signup
    **PATH:** `/api/auth/signup/`
    <hr/>
    
    ### **BODY**
    
    * email (required)
    * phoneNumber (optional)
    * password (required)
    * password2 (required)

    ### <span style="color:lightgreen">**SUCCESS - HTTP_201**</span>
    - `{
        "email": "<email>",
        "phoneNumber": "<phoneNumber>"
    }`

    ### <span style="color:red">**ERROR - HTTP_400**</span>
    - `{ "email": [
            "user with this email already exists."
        ]
    }`
    - `{ "email": [
            "Enter a valid email address."
        ]
    }`
    - `{ "nonFieldErrors": [
            "Passwords don't match!"
        ]
    }`

<br/>

- ## <span style="color:orange">**POST**</span> Login
    **PATH:** `/api/auth/get-token/`
    <hr/>
    
    ### **BODY**
    
    * email (required)
    * password (required)

    ### <span style="color:lightgreen">**SUCCESS - HTTP_200**</span>
    - `{
        "refresh": "<JWT>",
        "access": "<JWT>"
    }`

    ### <span style="color:red">**ERROR - HTTP_401**</span>
    - `{
        "detail": "No active account found with the given credentials"
    }`

<br/>

- ## <span style="color:rgb(80,100,200)">**PATCH**</span> Change email
    **PATH:** `/api/auth/change-email/`
    <hr/>
    
    ### **HEADERS**
    - Authorization: "JWT \<jwt-token\>"

    ### **BODY**
    * email (required)

    ### <span style="color:lightgreen">**SUCCESS - HTTP_200**</span>
    - `{
        "email": "admin@admin.com"
    }`

    ### <span style="color:red">**ERROR - HTTP_400**</span>
    - `{
        "detail": [
            "user with this email already exists."
        ]
    }`

<br/>

- ## <span style="color:rgb(80,100,200)">**PATCH**</span> Change password
    **PATH:** `/api/auth/change-password/`
    <hr/>

    ### **HEADERS**
    - Authorization: "JWT \<jwt-token\>"
    
    ### **BODY**
    
    * password (required)
    * newPassword (required)
    * newPassword2 (required)

    ### <span style="color:lightgreen">**SUCCESS - HTTP_200**</span>
    - `{
        "message": "Successfully changed password."
    }`

    ### <span style="color:red">**ERROR - HTTP_400**</span>
    - `{
        "detail": [
            "Old password is incorrect!"
        ]
    }`
    - `{
        "detail": [
            "New passwords don't match!"
        ]
    }`

<br/>

- ## <span style="color:rgb(0,220,30)">**GET**</span> Get user settings
    **PATH:** `/api/users/settings/`
    <hr/>

    ### **HEADERS**
    - Authorization: "JWT \<jwt-token\>"

    ### <span style="color:lightgreen">**SUCCESS - HTTP_200**</span>
    - `{
        "email": "admin@admin.com",
        "firstName": "Admin",
        "lastName": "Adminovich",
        "phoneNumber": "15487711"
    }`

    ### <span style="color:red">**ERROR - HTTP_401**</span>
    - `{
        "detail": "Authentication credentials were not provided."
    }`

<br/>

- ## <span style="color:rgb(0,100,255)">**PUT**</span>/<span style="color:rgb(80,100,200)">**PATCH**</span> Update user settings
    **PATH:** `/api/users/settings/`
    <hr/>

    ### **HEADERS**
    - Authorization: "JWT \<jwt-token\>"

    ### **BODY**
    
    * firstName (optional)
    * lastName (optional)
    * phoneNumber (optional)

    ### <span style="color:lightgreen">**SUCCESS - HTTP_200**</span>
    - `{
        "email": "admin@admin.com",
        "firstName": "Admin",
        "lastName": "Adminovich",
        "phoneNumber": "15487711"
    }`

    ### <span style="color:red">**ERROR - HTTP_401**</span>
    - `{
        "detail": "Authentication credentials were not provided."
    }`