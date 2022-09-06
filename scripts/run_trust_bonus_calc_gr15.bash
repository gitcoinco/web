#!/bin/bash

sudo docker-compose -f docker-compose-celery.yml exec -T worker_1 python3.7 manage.py compute_gr15_trust_bonus
