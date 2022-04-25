FROM python:3
RUN pip install https://github.com/prominence-eosc/cli/archive/refs/heads/main.zip
ENTRYPOINT ["/usr/local/bin/prominence"]
