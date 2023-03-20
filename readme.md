# Shorty - simple example of UrlShortener API, build on FastAPI ![Test](coverage-badge.svg)
# Description
- Simple UrlShortener. Build with FastAPI framework and using SQlite as local DB
- Functionally allows to create **random** short version of provided Url with chosen **length**
  , or by using **custom** names and redirecting from them
- For documentation simply insert - **/docs** at the end of the local path after **setting it up**
# Setup
    Local with uvicorn
      1. install 
    pip install -r requirements.txt
        2. Set your env-variables:
              EMAIL - any Gmail account
              EMAIL_KEY - any Gmail third party access key
              ADMIN_KEY - any access key
              (if not set REGISTER/DELETE won't be functional)
          3. uvicorn shorty:shorty --reload
      Local with Docker
        1. create .env
        2. from shorty.py dir
        run:
          docker-compose up 
                  (5000/port by default)
# Tests

- Simple Unit Testing with good coverage


    
    from shorty.py dir
    run:
      pytest
      pytest --cov