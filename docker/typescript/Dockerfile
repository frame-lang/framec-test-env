FROM node:20-slim

# Install framec binary
COPY framec /usr/local/bin/framec
RUN chmod +x /usr/local/bin/framec

# Create working directories
RUN mkdir -p /tests /tmp/out

# Install ts-node globally
RUN npm install -g ts-node typescript @types/node

# Copy entry script
COPY run_tests.sh /run_tests.sh
RUN chmod +x /run_tests.sh

WORKDIR /tests

ENTRYPOINT ["/run_tests.sh"]
