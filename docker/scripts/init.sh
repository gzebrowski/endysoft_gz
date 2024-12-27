#!/bin/bash

cd /usr/src/app || exit

echo "Collecting static files...";
mkdir -p /usr/src/app/static_collected
python manage.py collectstatic --noinput --skip-checks
collectstatic_status=$?
if [[ $collectstatic_status -eq 0 ]]; then
  echo "Static files collected!";
else
  echo 'Collecting static files failed!';
  exit 1;
fi

echo "Create admin if there is no active superuser yet...";
python manage.py addsuperuser --email=$ADMIN_EMAIL --password=$ADMIN_PASSWORD
addsuperuser_status=$?
if [[ $addsuperuser_status -eq 0 ]]; then
  echo "Admin is ready...";
else
  echo 'Error! Could not create admin.';
  exit 1;
fi
