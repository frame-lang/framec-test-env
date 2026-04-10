FROM mcr.microsoft.com/dotnet/sdk:8.0
RUN mkdir -p /tests /output /tmp/csproject && \
    cd /tmp/csproject && dotnet new console --force && \
    rm Program.cs
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["csharp"]
