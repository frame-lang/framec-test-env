FROM python:3.12-slim
RUN mkdir -p /tests /output /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/python_batch.sh /python_batch.sh
COPY runners/TestRunner.py /opt/TestRunner.py
RUN chmod +x /runner.sh /python_batch.sh /opt/TestRunner.py /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["python"]
