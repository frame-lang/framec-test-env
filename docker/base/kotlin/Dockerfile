FROM eclipse-temurin:21-jdk
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip && \
    curl -sL "https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip" -o /tmp/kotlin.zip && \
    unzip -q /tmp/kotlin.zip -d /opt && \
    ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin && \
    rm /tmp/kotlin.zip && \
    mkdir -p /tests /output /lib && \
    curl -sL "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar" -o /lib/json.jar && \
    curl -sL "https://repo1.maven.org/maven2/org/jetbrains/kotlinx/kotlinx-coroutines-core-jvm/1.8.1/kotlinx-coroutines-core-jvm-1.8.1.jar" -o /lib/kotlinx-coroutines-core-jvm.jar && \
    curl -sL "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.16.1/jackson-core-2.16.1.jar" -o /lib/jackson-core.jar && \
    curl -sL "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.16.1/jackson-annotations-2.16.1.jar" -o /lib/jackson-annotations.jar && \
    curl -sL "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.16.1/jackson-databind-2.16.1.jar" -o /lib/jackson-databind.jar && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/kotlin_batch.sh /kotlin_batch.sh
COPY runners/TestRunner.kt /tmp/TestRunner.kt
RUN chmod +x /runner.sh /kotlin_batch.sh /framec_cached.sh && \
    kotlinc /tmp/TestRunner.kt -include-runtime -d /opt/test_runner.jar && \
    rm /tmp/TestRunner.kt
ENTRYPOINT ["/runner.sh"]
CMD ["kotlin"]
