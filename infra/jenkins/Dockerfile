FROM jenkins/jenkins:lts

USER root

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    python3 \
    python3-venv \
    python3-pip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (with explicit version and proper PATH setup)
ENV POETRY_HOME="/opt/poetry"
ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod +x ${POETRY_HOME}/bin/poetry
RUN ln -s /usr/local/bin/poetry /usr/bin/poetry || true

# Install Sonar Scanner CLI
RUN curl -sSLo /tmp/sonar.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip \
    && unzip /tmp/sonar.zip -d /opt \
    && mv /opt/sonar-scanner-* /opt/sonar-scanner \
    && ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner \
    && rm /tmp/sonar.zip

# CRITICAL: Add jenkins user to docker group
RUN groupadd -g 999 docker || true \
    && usermod -aG docker jenkins

# Switch back to jenkins user
USER jenkins

# Add poetry to jenkins user's PATH
ENV PATH="/opt/poetry/bin:${PATH}"