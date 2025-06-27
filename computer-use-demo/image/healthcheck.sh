#!/bin/bash
# A more robust healthcheck for the noVNC server

# Try to connect for up to 45 seconds
for i in {1..45}; do
    # Use curl to silently check the noVNC web server.
    # The -s flag is for silent, -f makes it fail on server errors.
    if curl -s -f http://localhost:8080 > /dev/null; then
        # If curl succeeds, the server is up. Exit with success code 0.
        echo "Healthcheck: noVNC server is responsive."
        exit 0
    fi
    echo "Healthcheck: Waiting for noVNC server..."
    sleep 1
done

# If the loop finishes without success, exit with failure code 1.
echo "Healthcheck: noVNC server failed to start in time."
exit 1