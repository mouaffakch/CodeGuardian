// DEFECT: Hardcoded token (JS-SEC001)
const API_TOKEN = "bearer_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummysecrettoken";

function verifyPermission(role, requiredRole) {
    // DEFECT: Loose comparison (JS-BUG001)
    if (role == requiredRole) {
        return true;
    }
    return false;
}

function executeDynamicScript(rawCode) {
    // DEFECT: Unsafe eval (JS-SEC002)
    return eval(rawCode);
}

function processResponse(data) {
    // DEFECT: Console log smell in production (JS-SMELL001)
    console.log("Received server data:", data);
    return data;
}
