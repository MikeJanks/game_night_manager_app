/**
 * @param {string | undefined | null} text
 * @returns {string}
 */
export function getInitials(text) {
  const parts = String(text || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (parts.length === 0) return "??"
  if (parts.length === 1) return parts[0]?.[0]?.toUpperCase() || "?"

  const first = parts[0]?.[0] || ""
  const last = parts[parts.length - 1]?.[0] || ""

  return `${first}${last}`.toUpperCase()
}
