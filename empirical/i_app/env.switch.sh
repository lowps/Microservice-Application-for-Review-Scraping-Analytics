#!/bin/bash

# Usage: ./env.switch.sh dev
# or    ./env.switch.sh prod

# Check if script is being sourced
(return 0 2>/dev/null)
if [ $? -ne 0 ]; then
  echo "Please run this script with 'source ./env.switch.sh [dev|prod]'"
  exit 1
fi

ENV=$1

if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
  echo "Usage: source $0 [dev|prod]"
  return 1
fi

export DJANGO_ENV=$ENV

if [[ "$ENV" == "prod" ]]; then
  export DJANGO_SETTINGS_MODULE="app.settings.production"
else
  export DJANGO_SETTINGS_MODULE="app.settings.local"
fi

echo "DJANGO_ENV set to $DJANGO_ENV"
echo "DJANGO_SETTINGS_MODULE set to $DJANGO_SETTINGS_MODULE"
echo "Now enviornment is ready to run the python manage.py runserver command"

