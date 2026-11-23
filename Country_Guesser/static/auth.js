async function request(method, url, body) {
    const response = await fetch(url, {
        method,
        headers: {"Content-Type": "application/json"},
        body: body ? JSON.stringify(body): undefined
    });
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || response.statusText);
    return data;
}

export const register = (user)            => request("POST", "/users", user);
export const login = (email, password)    => request("POST", "/sessions", { email, password});
export const logout = ()                  => request("DELETE", "/sessions");
export const getCurrentUser = ()          => request("GET", "/sessions/current");
