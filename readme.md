# Shorty - simple example of UrlShortener API, build on FastAPI ![Test](coverage-badge.svg)
# Description
- Simple UrlShortener. Build with FastAPI framework and using SQlite as local DB
---------------------
- Functionally allows:
  - create **random** short version of provided **Url** with chosen **length** to redirect from
  - create **custom** named Urls and **redirect** from them
  - create **api-key** to expand expire limits and associate **custom** Urls with that key
---------------------
- For documentation simply add - **/docs** at the end of the **path** after **setting it up** (based on [:blue_book:](https://fastapi.tiangolo.com/advanced/extending-openapi/))
# Setup
  Locally with Uvicorn
      

    1. install dependencies:
      run
      python -m pip install -r requirements.txt
    2. set your env-variables:
      $EMAIL - any Gmail account
      $EMAIL_KEY - any Gmail third party access key
      $ADMIN_KEY - any access key
        (if not set REGISTER/DELETE won't be functional)
    3. start Uvicorn: 
      run
        python -m uvicorn shorty:shorty

Locally with Docker
           

    1. create .env
    2. add variables
    3. from shorty.py directory:
      run
        docker-compose up 
               (5000/port by default)
# Tests

- Simple Unit Testing with good coverage



    1. set ENV
    2. from shorty.py directory:
      run
        python -m pytest


# TODO/REDO
- add home-page with UI
- almost all tests need's to be redone. Second attempt at writing tests, it's fine but very hardcoded.
- make tests more universal
- make more universal functions, there's 3+ repeats of same functionality for no reason
- better not use **local** DB's if I want to host api easier