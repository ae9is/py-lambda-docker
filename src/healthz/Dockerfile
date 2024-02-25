FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt ./
RUN python3.11 -m pip install --no-cache-dir --disable-pip-version-check -U -r requirements.txt
COPY app.py ./

CMD ["app.handler"]
 