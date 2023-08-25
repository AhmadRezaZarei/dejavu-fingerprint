#!/bin/bash
flask --app main run --host=0.0.0.0

import mysql.connector
mysql.connector.connect(host="db", database="dejavu", password="PnKKvj21RziO2OKf", user="root")