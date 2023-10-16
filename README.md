
# QSMR lambda images

Qsmr as a AWS lambda function. The lambdas expect an event:

    {
        "source": <url>,
        "target": <url>
    }


## Test as lambda function

    docker build -f Dockerfile.stnd1 -t qsmr .

    mkdir -p ~/.aws-lambda-rie \
    && curl -Lo ~/.aws-lambda-rie/aws-lambda-rie \
        https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie \
    && chmod +x ~/.aws-lambda-rie/aws-lambda-rie

    docker run --rm \
        -v ~/.aws-lambda-rie:/aws-lambda \
        -p 9000:8080 \
        --entrypoint /aws-lambda/aws-lambda-rie \
        qsmr npx aws-lambda-ric app.handler

    curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
        -d '{\
            "source":\
                "https://odin-smr.org/rest_api/v4/freqmode_info/2015-04-01/AC2/1/7123991206/", \
            "target":"https://enp5nczv3p7f.x.pipedream.net/"}'


## Test matlab runtime

    docker build -f Dockerfile.stnd1 -t qsmr .

    docker run --rm -ti --entrypoint="" qsmr bash

    LD_LIBRARY_PATH=/opt/matlab/v90/runtime/glnxa64:/opt/matlab/v90/bin/glnxa64:/opt/matlab/v90/sys/os/glnxa64 \
    ./run_runscript.sh /opt/matlab/v90/ \
    "https://odin-smr.org/rest_api/v4/freqmode_info/2015-04-01/AC2/1/7123991206/" \
    "https://enp5nczv3p7f.x.pipedream.net/"

