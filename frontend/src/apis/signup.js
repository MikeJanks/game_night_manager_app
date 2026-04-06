/**
 * @param {{ username: string, email: string, password: string }} payload
 * @returns {Promise<unknown>} Parsed JSON user payload from FastAPI Users register.
 */
export default async function signup(payload) {
  const res = await fetch(`/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: payload.username,
      email: payload.email,
      password: payload.password,
    }),
  });
  if (!res.ok) {
    let message = "Signup failed";
    try {
      const err = await res.json();
      if (typeof err.detail === "string") message = err.detail;
      else if (Array.isArray(err.detail))
        message = err.detail.map((e) => e.msg ?? JSON.stringify(e)).join(", ");
    } catch { }
    throw new Error(message);
  }
  return res.json();
}
