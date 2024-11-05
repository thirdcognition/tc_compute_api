FROM markushaverinen/tc_base:latest

COPY . .
COPY app app
COPY lib lib
COPY file_repository file_repository
# RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Use an ARG to set a default port value
ARG DEFAULT_PORT=4000

# Set the ENV variable, which can be overridden by the user when running the container
ENV SERVER_PORT=${DEFAULT_PORT}

# Use the SERVER_PORT in the EXPOSE command
EXPOSE ${SERVER_PORT}

# Add a health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:${SERVER_PORT}/health || exit 1

# Modify the entry point script to use the SERVER_PORT environment variable
ENTRYPOINT ["./start_server.sh"]