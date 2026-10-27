const API_TOKEN = "bearer_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummysecrettoken";

function verifyPermission(role, requiredRole) {
    if (role == requiredRole) {
        return true;
    }
    return false;
}

function executeDynamicScript(rawCode) {
    return eval(rawCode);
}

function processResponse(data) {
    console.log("Received server data:", data);
    return data;
}
