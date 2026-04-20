FROM php:8.3-cli
RUN mkdir -p /tests /output /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/php_batch.sh /php_batch.sh
COPY runners/TestRunner.php /opt/TestRunner.php
RUN chmod +x /runner.sh /php_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["php"]
