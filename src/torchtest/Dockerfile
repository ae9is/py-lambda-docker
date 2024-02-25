# Note: Amazon Linux 2 only ships with glibc 2.26; pytorch requires glibc 2.27+ and python <= 3.11
FROM public.ecr.aws/lambda/provided:al2023
RUN dnf install -y python3.11
RUN python3.11 -m ensurepip
RUN dnf clean all

WORKDIR ${LAMBDA_TASK_ROOT}
RUN python3.11 -m pip install --no-cache-dir --disable-pip-version-check -U awslambdaric
COPY requirements.txt ./
RUN python3.11 -m pip install --no-cache-dir --disable-pip-version-check -U -r requirements.txt
COPY app.py ./

ENTRYPOINT [ "/usr/bin/python3.11", "-m", "awslambdaric" ]
CMD ["app.handler"]
