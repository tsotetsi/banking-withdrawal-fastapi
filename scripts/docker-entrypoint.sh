#!/bin/sh

set -e

# essential services (DB, Message Queue/Broker).
CRITICAL_VARS="DATABASE_URL AWS_ENDPOINT_URL WITHDRAWAL_TOPIC_ARN"

echo "========================================================================"
echo "Starting Application Startup Checks..."
echo "------------------------------------------------------------------------"

MISSING=0

for VAR_NAME in $CRITICAL_VARS; do
  # Check if the variable is unset or empty.
  if [ -z "$(eval echo "\$$VAR_NAME")" ]; then
    echo "🚨 ERROR: Missing critical environment variable: $VAR_NAME"
    MISSING=1
  fi
done

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "         CONTAINER STARTUP FAILED DUE TO MISSING CONFIGURATION"
  echo "------------------------------------------------------------------------"
  echo "ACTION REQUIRED: The application failed to load critical configuration."
  echo "If running with Docker Compose, this usually means the **.env** file is"
  echo "missing. Please create a **.env** file by copying the contents"
  echo "of **.env.example** in the root of your project."
  echo "========================================================================"
  exit 1
fi

echo "✅ All critical environment variables found. Proceeding with CMD..."
echo "========================================================================"

exec "$@"