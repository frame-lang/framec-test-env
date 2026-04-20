FROM ruby:3.3-slim
RUN mkdir -p /tests /output /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/ruby_batch.sh /ruby_batch.sh
COPY runners/TestRunner.rb /opt/TestRunner.rb
RUN chmod +x /runner.sh /ruby_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["ruby"]
