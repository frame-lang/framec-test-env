# Frame VS Code Extension Debugger Test Environment
# Follows segregation policy: frame-debugger-* namespace

FROM ubuntu:22.04 AS base

# Labels for segregation
LABEL frame.component=debugger
LABEL frame.team=extension
LABEL frame.purpose=testing
LABEL maintainer="Frame VS Code Extension Team"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV FRAME_TEST_NAMESPACE=debugger

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    git \
    curl \
    wget \
    # Python and pip (for Frame debugging)
    python3 \
    python3-pip \
    python3-venv \
    # Node.js prerequisites
    ca-certificates \
    gnupg \
    # X11 dependencies for VS Code testing (headless)
    xvfb \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    # Additional utilities
    dos2unix \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Stage 2: Development environment
FROM base AS development

# Set working directory to /debugger namespace
WORKDIR /debugger

# Copy package files first for better caching
COPY package*.json ./

# Install Node dependencies
RUN npm ci

# Copy TypeScript config and source files
COPY tsconfig.json ./
COPY .eslintrc.json ./

# Copy application source (will be mounted as volume in runtime)
COPY src/ ./src/
COPY media/ ./media/
COPY framec/ ./framec/
COPY scripts/ ./scripts/
COPY images/ ./images/

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.js 2>/dev/null || true

# Build the extension
RUN npm run compile

# Stage 3: Testing environment
FROM development AS testing

# Install VS Code test dependencies
RUN npm install -g @vscode/test-electron

# Python debug runtime dependencies
RUN pip3 install --no-cache-dir \
    debugpy \
    typing_extensions

# Create test directories with proper namespacing
RUN mkdir -p /debugger/tests \
    /debugger/fixtures \
    /debugger/results \
    /debugger/builds \
    /debugger/test-frames \
    /debugger/.vscode-test

# Set permissions for test user
RUN useradd -m -s /bin/bash debugger-test && \
    chown -R debugger-test:debugger-test /debugger

# Switch to non-root user for testing
USER debugger-test

# Environment variables for testing
ENV NODE_ENV=test
ENV DISPLAY=:99
ENV ELECTRON_DISABLE_SANDBOX=1
ENV FRAME_TEST_MODE=docker
ENV FRAME_TEST_COMPONENT=vscode-extension
ENV FRAME_DEBUGGER_VERSION=0.12.216

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "console.log('healthy')" || exit 1

# Entry point for running tests
ENTRYPOINT ["xvfb-run", "-a", "--server-args=-screen 0 1024x768x24"]
CMD ["npm", "test"]