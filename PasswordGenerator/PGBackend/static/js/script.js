const apiUrl = "http://127.0.0.1:5000/api";  // Ensure it's using /api endpoints

document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("register-username").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value.trim();
    const confirmPassword = document.getElementById("confirm-password").value.trim();

    if (!username || !email || !password || !confirmPassword) {
        alert("All fields are required!");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert("Registration successful! Redirecting to login...");
            window.location.href = "/";
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to register. Please try again.");
    }
});

// Handle login
document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    if (!username || !password) {
        alert("Username and password are required!");
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert("Login successful! Redirecting to password generator...");
            window.location.href = "/api/generator";
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to log in. Please try again.");
    }
});

// Handle password generation
document.addEventListener("DOMContentLoaded", function () {
    const passwordDisplay = document.getElementById("generatedPassword");

    document.getElementById("generator-form").addEventListener("submit", async function (event) {
        event.preventDefault();

        const length = document.getElementById("passwordLength").value;
        const formatSelected = document.getElementById("passwordFormat").value;

        if (length < 6) {
            passwordDisplay.textContent = "Password length must be at least 6!";
            return;
        }

        try {
            const response = await fetch("/api/generate-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ length: parseInt(length), format: formatSelected })
            });

            const data = await response.json();

            if (response.ok) {
                passwordDisplay.textContent = `Generated Password: ${data.password}`;
            } else {
                passwordDisplay.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            console.error("Error generating password:", error);
            passwordDisplay.textContent = "Failed to generate password. Try again.";
        }
    });

    // Handle password download
    document.getElementById("download-btn").addEventListener("click", function () {
        window.location.href = "/api/download-passwords";
    });

    // Handle clearing passwords
    document.getElementById("clear-btn").addEventListener("click", async function () {
        try {
            const response = await fetch("/api/clear-passwords", { method: "POST" });
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error("Error clearing passwords:", error);
            alert("Failed to clear passwords.");
        }
    });
});

document.getElementById("logout-btn")?.addEventListener("click", () => {
    fetch("/logout", { method: "GET" })
        .then(() => {
            window.location.href = "/";
            setTimeout(() => {
                window.location.reload(true);  // Force full reload
            }, 100);
        })
        .catch(error => console.error("Logout error:", error));
});

