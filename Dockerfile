FROM python:3
RUN pip install https://github.com/prominence-eosc/cli/archive/master.zip
ENTRYPOINT ["/usr/local/bin/prominence"]
