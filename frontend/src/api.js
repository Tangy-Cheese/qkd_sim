// Every call to the FastAPI backend goes through here.
// In dev, vite proxies /api to uvicorn (see vite.config.js). Set VITE_API_URL to talk to a backend somewhere else.
const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

// FastAPI sends a string for HTTPException and a list of {loc, msg} for validation (422) errors
function describeDetail(detail) {
    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map((d) => {
                const field = (d.loc ?? []).filter((part) => part !== "body").join(".");
                return field ? `${field}: ${d.msg}` : d.msg;
            })
            .join("; ");
    }

    return null;
}

async function request(path, options = {}) {
    let response;

    try {
        response = await fetch(API_BASE + path, options);
    } catch (err) {
        if (err.name === "AbortError") {
            throw err;
        }
        throw new ApiError("Cannot reach the backend. Is uvicorn running on port 8000?", 0);
    }

    let data = null;
    try {
        data = await response.json();
    } catch {
        // no JSON body, e.g. the proxy answering for a backend that is down
    }

    if (!response.ok) {
        const message = describeDetail(data?.detail)
            ?? `Backend did not answer properly (HTTP ${response.status}). Is uvicorn running on port 8000?`;
        throw new ApiError(message, response.status);
    }

    return data;
}

function post(path, body, signal) {
    return request(path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
        signal,
    });
}

export function runBB84(params, signal) {
    return post("/protocols/bb84", { protocol: "BB84", ...params }, signal);
}

export function runE91(params, signal) {
    return post("/protocols/e91", { protocol: "E91", ...params }, signal);
}

export function runSimulation(params, signal) {
    return post("/simulation", params, signal);
}

export function getDefaultNetwork(signal) {
    return request("/network/default", { signal });
}
