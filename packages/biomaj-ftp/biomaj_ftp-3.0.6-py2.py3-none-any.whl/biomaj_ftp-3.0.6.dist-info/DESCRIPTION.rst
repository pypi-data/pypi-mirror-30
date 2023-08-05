# Biomaj ftp

Biomaj FTP server to access production banks

anonymous access is allow with login *anonymous* and any fake password.
Existing users can access server with the login and API key as password.

Only public or owned banks are accessible

# Config

config.yml contains the server configuration.
Mongo configuration should be the same one than biomaj.

Web endpoint refers to the biomaj API endpoint

# Run

export BIOMAJ_CONFIG=path_to_config.yml

python bin/biomaj_ftp_service.py

# Docker

To run in a Docker container, do not forget to open passive ports range (60000, 65535)


3.0.6:
  Add ftp/masquerade_address in config or MASQUERADE_ADDRESS env variable to define address ftp server should advertise (mainly for docker)
3.0.5:
  Allow proxy endpoint definition for daemon, else use default web.local_endpoint
3.0.4:
  Add passive ports setup, range(60000, 65535)
  Modify login: use login and api key to access to all available banks instead of connecting to one bank
3.0.3:
  Set consul checks
3.0.2:
  Allow override of config
  Fix user authentication
  Load database settings from global.properties to match same database than biomaj
3.0.1:
  Fix anonymous access and case where web/local_endpoint is not defined in config.yml
3.0.0:
  FTP server to access banks


