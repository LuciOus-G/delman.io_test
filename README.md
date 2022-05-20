
# Running the app

To running the app it's simple just run ```docker-compose -f delmanio.yml up```

enter the project ```cd delmanio``` and run ```docker-compose -f delmanio.yml up```,
there will be 3 sevices

1. postgresql
2. pgadmin4
3. web services

the web services running on ip ```localhost:5000```
the pgadmin4 running on ip ```localhost:8080```
and for database there are 2 type of host, if you want to connect outside the docker use ```localhost:5433```
but if you use the database inside the docker use ```db:5432```

# Running the unit test
To running the app it's simple just run ```docker-compose -f delmanio_test.yml up```

enter the project ```cd delmanio``` and run ```docker-compose -f delmanio_test.yml up```