export function capitalizeFirstLetter(val: string | number): string {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}
