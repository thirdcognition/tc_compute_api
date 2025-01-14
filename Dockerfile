FROM markushaverinen/tc_ms_poc_base:latest

COPY . .
COPY app app
COPY source source
COPY file_repository file_repository
COPY static static

# Set environment variables for React applications
ENV REACT_APP_GA_MEASUREMENT_ID=${GA_MEASUREMENT_ID}
ENV REACT_APP_DEBUG_MODE=${DEBUG_MODE}
ENV REACT_APP_PORT=${SERVER_PORT}

WORKDIR /static/admin
RUN npm install
RUN npm run build
WORKDIR /

# Install and build for /static/player/
WORKDIR /static/player
RUN npm install
RUN npm run build
WORKDIR /

RUN chmod +x start_server.sh
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

RUN --mount=type=cache,target=/root/.cache/ms-playwright playwright install --with-deps

# Modify the entry point script to use the SERVER_PORT environment variable
ENTRYPOINT ["./start_server.sh"]
