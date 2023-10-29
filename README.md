
# QSMR images

Qsmr runs in a docker container. The entrypoint script consumes messages 
from the queue named in the `QUEUE_NAME` environmental parameter.


## Deployment

Manual deployment.

1. Build images
    
        ./build

2. Force new deployment of services in AWS console
