export const config = {
    protocol: window.location.protocol,
    hostname: window.location.hostname,
    port: ":4000" // window.location.port ? `:${window.location.port}` : ""
};

export function replaceLocalhostUrl(url: string): string {
    return url.replace(
        "http://127.0.0.1:4000",
        `${config.protocol}//${config.hostname}${config.port ? `:${config.port}` : ""}`
    );
}

export function urlFormatter(
    urls: Record<string, string>
): Record<string, string> {
    return urls
        ? Object.fromEntries(
              Object.entries(urls).map(([id, url]) => [
                  id,
                  replaceLocalhostUrl(url)
              ])
          )
        : {};
}
