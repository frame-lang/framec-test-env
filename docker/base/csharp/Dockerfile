FROM mcr.microsoft.com/dotnet/sdk:8.0
RUN mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/csharp_batch.sh /csharp_batch.sh
COPY runners/TestRunner.cs /opt/testrunner/TestRunner.cs
COPY runners/TestRunner.csproj /opt/testrunner/TestRunner.csproj
RUN chmod +x /runner.sh /csharp_batch.sh /framec_cached.sh && \
    mkdir -p /opt/testrunner/tests && \
    # Warm up the NuGet cache so the first real build doesn't pay restore
    # cost. A stub .cs file keeps the glob+compile happy.
    printf 'namespace __warmup { class _Stub {} }\n' > /opt/testrunner/tests/_warmup.cs && \
    dotnet build /opt/testrunner -c Release --nologo >/dev/null && \
    rm /opt/testrunner/tests/_warmup.cs
ENTRYPOINT ["/runner.sh"]
CMD ["csharp"]
