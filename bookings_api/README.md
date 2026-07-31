## How to run setup and run tests (ubuntu)
1) Make sure python and pip is installed
2) make sure you are in directory bookings_api
4) run command for activating virtual environment
- source ve/bin/activate
5) run command to run REQUIREMENTS
- pip install -r REQUIREMENTS.txt
6) run command to run tests
- cd booking_system && pytest
7) run command for running the server
- cd booking_system && python3 manage.py runserver
8) if your python points to python3 you can use command for running server
- cd booking_system && python manage.py runserver


## How to run setup and run tests (windows)
1) Make sure python and pip is installed
2) make sure you are in directory bookings_api
4) run command for activating virtual environment
- . ve\bin\activate
5) run command to run REQUIREMENTS
- pip install -r .\REQUIREMENTS.txt
6) run command to run tests
- cd booking_system 
- pytest
7) run command for running the server
- cd booking_system 
- python3 manage.py runserver
8) if your python points to python3 you can use command for running server
- cd booking_system 
- python manage.py runserver