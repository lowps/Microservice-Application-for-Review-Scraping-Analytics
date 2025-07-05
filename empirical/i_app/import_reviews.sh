#!/bin/bash

# Run the import command
python manage.py import_reviews "/Users/ericklopez/desktop/django_gun/empirical/f_data/final/starbucks_location_newYorkCity_final.csv" --business_name "STARBUCKS" --source "GOOGLE MAPS"

echo "Reviews imported successfully!"
