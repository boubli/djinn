FROM python:3.10-slim

WORKDIR /app

# Install git as it is often needed for plugins/updates
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install djinn-cli
RUN pip install --no-cache-dir djinn-cli

# Set entrypoint
ENTRYPOINT ["djinn"]
CMD ["--help"]
