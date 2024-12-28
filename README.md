# Tenant application

## install

Copy the `.env.example` file to `.env` and set the environment variables.


### install via docker

Just run command: `./bin/build`

### install via virtualenv

- Install python3.11
- install virtual environment by running command: `python3.11 -m venv venv`
- activate the virtual environment by running command: `source venv/bin/activate`
- install the dependencies by running command: `pip install -r requirements_dev.txt`
- change directory to src by running command: `cd src`
- run migrations by running command: `python manage.py migrate`
- create superuser by running command: `python manage.py createsuperuser`
- run the server by running command: `python manage.py runserver`

there are two frontend pages available:
- admin interface: `http://localhost:8000/admin/`
- api schema: `http://localhost:8000/schema/swagger-ui/`

### Running the tests

To run the tests, run the command: `pytest -v .`
 
### Evaluating the API

You can evaluate the API by visiting the `http://localhost:8000/schema/swagger-ui/` endpoint.
To create a new user you can post endpoint `/api/users/signup/`
To login you can post endpoint `/api/users/login/`

In both cases you will receive in the json response a token that you can use to authenticate in the other endpoints.
To authenticate just click on the `Authorize` button and add  in the `Value` field type `Token <token>` 
where `<token>` is the token you received in the response of the login or signup endpoint.

The next step is to create a tenant by posting in the endpoint `/api/tenants/` with the following payload:
```
{
    "name": "tenant_name",
    "domain": "tenant_domain"
}
```

Once the tenant is created you will have to use the tenant domain in the header called `X-Tenant-Name` to 
authenticate in the other endpoints. This header is required in all the endpoints that are related to the tenant.

## brief explanation of the architecture

There are only two applications in the project: `users` and `tenants`. 
Users just have the signup and login endpoints.
Tenants application has 5 models: `Tenant`, `TenantUser`, `Organization`, `Department` and `Customer`.
Three models: `Organization`, `Department` and `Customer` are isolated by tenant.
The isolation is done by middleware that checks the header `X-Tenant-Name` and sets the tenant domain in the 
request object. Every model that has to be isolated by tenant has to derive from the `TenantIsolationMixIn` class.
A view class that has to be isolated by tenant has to be decorated with the `@tenant_isolation_view` decorator.
This decorator does some magic stuff such as injecting serializers, get_queryset and initial method to the view class
the check behind the scenes if the tenant is allowed to access the data.
