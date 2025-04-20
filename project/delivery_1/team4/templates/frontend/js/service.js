async function fetchService(service) {
    const respDiv = document.getElementById("service-response");
    respDiv.textContent = "Cargando...";

    const token = localStorage.getItem('token');

    if (token === null){
        respDiv.textContent = "No token"
        return;
    }

    try {
      const res = await fetch(`http://localhost:5000/${service}`, {
        headers: { 'Authorization': `Bearer ${token}` || '' }
      });
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      respDiv.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      respDiv.textContent = `Error: ${err.message}`;
    }
  }

  document.getElementById("btn-ms1").addEventListener("click", () => fetchService('ms-1'));
  document.getElementById("btn-ms2").addEventListener("click", () => fetchService('ms-2'));
