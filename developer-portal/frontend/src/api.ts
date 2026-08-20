export type Session = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Identity = {
  id: number;
  username: string;
  email: string;
  team: string;
  role: string;
  active: boolean;
};

const SESSION_KEY = "idp.portal.session";

export function getSession(): Session | null {
  const raw = localStorage.getItem(
    SESSION_KEY
  );

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as Session;
  } catch {
    localStorage.removeItem(
      SESSION_KEY
    );

    return null;
  }
}

export function saveSession(
  session: Session
) {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify(session)
  );
}

export function clearSession() {
  localStorage.removeItem(
    SESSION_KEY
  );
}

async function parseResponse(
  response: Response
) {
  if (response.status === 204) {
    return null;
  }

  const contentType =
    response.headers.get(
      "content-type"
    ) ?? "";

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    return response.json();
  }

  return response.text();
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true
): Promise<T> {
  const headers = new Headers(
    options.headers
  );

  if (
    options.body &&
    !headers.has("Content-Type")
  ) {
    headers.set(
      "Content-Type",
      "application/json"
    );
  }

  if (authenticated) {
    const session = getSession();

    if (session) {
      headers.set(
        "Authorization",
        `Bearer ${session.access_token}`
      );
    }
  }

  const response = await fetch(
    path,
    {
      ...options,
      headers,
    }
  );

  const payload =
    await parseResponse(response);

  if (!response.ok) {
    const detail =
      typeof payload === "object" &&
      payload !== null &&
      "detail" in payload
        ? JSON.stringify(
            payload.detail
          )
        : String(
            payload ||
              response.statusText
          );

    throw new Error(detail);
  }

  return payload as T;
}

export function portalGet<T>(
  path: string
) {
  return request<T>(
    `/api${path}`
  );
}

export function portalPost<T>(
  path: string,
  body: unknown
) {
  return request<T>(
    `/api${path}`,
    {
      method: "POST",
      body: JSON.stringify(body),
    }
  );
}

export async function login(
  username: string,
  password: string
) {
  const session =
    await request<Session>(
      "/identity/auth/token",
      {
        method: "POST",
        body: JSON.stringify({
          username,
          password,
        }),
      },
      false
    );

  saveSession(session);

  return session;
}

export async function logout() {
  const session = getSession();

  if (session) {
    try {
      await request(
        "/identity/auth/logout",
        {
          method: "POST",
          body: JSON.stringify({
            refresh_token:
              session.refresh_token,
          }),
        },
        false
      );
    } catch {
      // Local session cleanup remains authoritative.
    }
  }

  clearSession();
}

export function currentIdentity() {
  return portalGet<Identity>(
    "/portal/me"
  );
}
