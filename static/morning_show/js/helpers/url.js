export function replaceLocalhostUrl(url) {
    return url.replace(
        "http://127.0.0.1:4000",
        `${window.location.protocol}//${window.location.hostname}${window.location.port ? `:${window.location.port}` : ""}`
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
