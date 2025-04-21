let token = null;

async function login() {
  const user = document.getElementById("username").value;
  const pass = document.getElementById("password").value;
  const statusDiv = document.getElementById("login-status");
  statusDiv.style.color = "green";
  statusDiv.textContent = "Logging in...";

  try {
    const res = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass })
    });

    if (!res.ok) throw new Error('Invalid credentials');

    const data = await res.json();
    token = data.token;

    if (token !== null)
        localStorage.setItem('token', token);

    statusDiv.textContent = 'Login successful';
    document.getElementById('btn-ms1').disabled = false;
    document.getElementById('btn-ms2').disabled = false;
  } catch (err) {
    statusDiv.style.color = "red";
    statusDiv.textContent = 'Login failed: ' + err.message;
  }
}

document.getElementById('btn-login').addEventListener('click', login);
