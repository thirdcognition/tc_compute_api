/**
 * Get the value of a cookie by name.
 * @param name - The name of the cookie.
 * @returns The value of the cookie, or undefined if not found.
 */
export function getCookie(name: string): string | undefined {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift();
}

/**
 * Set a cookie with a specified name, value, and expiration in days.
 * @param name - The name of the cookie.
 * @param value - The value of the cookie.
 * @param days - The number of days until the cookie expires.
 */
export function setCookie(name: string, value: string, days: number): void {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}
