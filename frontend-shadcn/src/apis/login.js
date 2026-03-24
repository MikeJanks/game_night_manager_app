/**
 * @param {{ username: string, password: string }} credentials
 *   Use email (or username) in `username` — FastAPI Users / OAuth2 expect that field name.
 * @returns {Promise<{ access_token: string, token_type: string }>}
 */
export default async function login(credentials) {
    const body = new URLSearchParams();
    body.set("username", credentials.username);
    body.set("password", credentials.password);
    const res = await fetch(`/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });
    if (!res.ok) {
      let message = "Login failed";
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