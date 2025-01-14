export const config = {
    protocol: window.location.protocol,
    hostname: window.location.hostname,
    port: process.env.REACT_APP_PORT || ":4000"
};

export function replaceLocalhostUrl(url) {
    const { protocol, hostname, port } = config;
    return url.replace(
        `http://127.0.0.1:${port}`,
        `${protocol}//${hostname}${port ? `:${port}` : ""}`
    );
}

export function urlFormatter(urls) {
    return urls
        ? Object.fromEntries(
              Object.entries(urls).map(([id, url]) => [
                  id,
                  replaceLocalhostUrl(url)
              ])
          )
        : {};
}
