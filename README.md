# Cornell Creatives API
A backend API for the Cornell Creatives App

The Cornell Creatives App connects users who wish to provide services with those
who require those services. For example, a user may want to find a photographer,
where they can do so by searching on the app.

The backend server stores all user information of the service providers, and
allows the app to search and filter these users to show them in the app. It also
provides authentication processes for service providers to remove or edit
the services they provide.

## API Specifications

Each user has a netid, name, avatar, a list of services (may be empty or more than one).

netid is a string representing a Cornell University netid and identifies the user.
Name is a string representing the name of the user
avatar is an integer representing the type of avatar for the user
Services is a list of strings that represent the services that each user provides.

The services of a user must be supported by our application (currently, the supported
services are photographer, programmer, and tutor, although this is subject to change)

They also have authentication data including their password, session token,
expiration time for their session token, and a renew token.

### Registering a User:
Request: POST /register/
Body:
  {
    "netid": <user input>,
    "password": <user input>,
    "name": <user input>,
    "avatar": <user input>,
    "services": [<user input>, <user input>, ...]
  }
Response:
  {
    "success": true,
    "netid": <netid>,
    "name": <name>,
    "avatar": <avatar>
    "services": [<service1>, <service2>],
    "session": <session token>,
    "expiration": <expiration of session token>,
    "renew": <renew token>
  }
Notes:
  - This request generates a user in the database
  - The "services" key is optional and will default to an empty list when not
    provided.
  - The "avatar" key is optional and will default to 0 when not provided
  - The request will throw an error in the following cases:
    - netid already taken and the user already exists
    - no netid/password/name key provided
    - one or more of the services in the list of services is not supported by
      the site

### User Login:
Request: POST /login/
Body:
  {
    "netid": <netid>,
    "password": <password>
  }
Response:
  {
    "session": <session token>,
    "expiration": <expiration of session token>,
    "renew": <renew token>
  }
Notes:
  - The request will throw an error in the following cases:
    - No netid/password provided
    - When the credentials are incorrect
  - This request should be used when the session/renew token is lost

### Renew Session:
Request: Post /renew/
Body:{"renew": <renew token>}
Response:
  {
    "session": <session token>,
    "expiration": <expiration of session token>,
    "renew": <renew token>
  }
Notes:
  - The request would generate a new session and renew token
  - The request will throw an error in the following cases:
    - Renew token not provided
    - Renew token is invalid

### Get specific User:
Request: GET /user/<netid>/
Response:
  {
    "success": true,
    "netid": <netid>,
    "name": <name>,
    "avatar": <avatar>
    "services": [<service1>, <service2>]
  }
Notes:
  - The request will thorw an error in the following cases:
    - User with the netid is not found

### Edit services of a specific user:
Request: POST /user/<netid>/services/
Header:
  Authentication: Bearer <session token>
Body:{"services": [<services1>, <service2>]}
Response:
  {
    "success": true,
    "netid": <netid>,
    "name": <name>,
    "avatar": <avatar>
    "services": [<service1>, <service2>]
  }
Notes:
  - The request will throw an error in the following cases:
    - Invalid Authentication Token
    - No Authentication Token in header
    - Authentication token expired
    - No service field provided
    - Service not provided by the app

### Delete services of a specific user:
Request: DELETE /user/<netid>/services/
Header:
  Authentication: Bearer <session token>
Body:{"services": [<services1>]}
Response:
  {
    "success": true,
    "netid": <netid>,
    "name": <name>,
    "avatar": <avatar>
    "services": [<service2>]
  }
Notes:
  - The request will throw an error in the following cases:
    - Invalid Authentication Token
    - No Authentication Token in header
    - Authentication token expired
    - No service field provided
    - Service not provided by the user and thus cannot be deleted

### Get all users that provide a specific service:
Request: GET /service/<service>/
Response:
  {
    "success": true,
    [
      {
      "netid": <netid1>,
      "name": <name1>,
      "avatar": <avatar1>
      "services": [<service1>, <service2>]
      },
      "netid": <netid2>,
      "name": <name2>,
      "avatar": <avatar2>
      "services": [<service1>, <service2>]
    ]
  }
Notes:
  - The request will never throw an error, but the list of users may be empty

### Get all the users that provide services outside the default services supported by the app
Request: GET /service/other/
Response:
  {
    "success": true,
    [
      {
      "netid": <netid1>,
      "name": <name1>,
      "avatar": <avatar1>
      "services": [<service1>, <service2>]
      },
      "netid": <netid2>,
      "name": <name2>,
      "avatar": <avatar2>
      "services": [<service1>, <service2>]
    ]
  }
Notes:
  - The request will never throw an error, but the list of users may be empty
  - Currently, the default services provided by the app are :
    ['tutor', 'photographer', 'chef', 'videographer', 'artist']
  - This route is provided for the "others" screen of the app
