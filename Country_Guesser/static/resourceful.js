// Parses a response. A 401 means the session is gone, so announce it (stupid.js listens for this).
async function parseResponse(response) {
    const data = await response.json();
    if (response.status === 401) {
        window.dispatchEvent(new Event("session-expired"));
    }
    if (!response.ok) {
        const error = new Error(data.error || response.statusText);
        error.status = response.status;
        throw error;
    }
    return data;
}

export function storeUserCountry(country) {
    const countryData = {
        common_name: country.getCommonName(),
        official_name: country.getOfficialName(),
        population: Math.round(country.getPopulation()),
        html_flag_code: country.getFlagHTML(),
        area: Math.round(country.getLandAreaMiles())
    };

    return fetch("/countries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(countryData)
    })
    .then(parseResponse)
    .then(data => {
        console.log("Country created:", data);
        document.getElementById("form").reset();
        // return listUserCountries();
    })
    .catch(error => {
        console.error("Error:", error);
        if (error.status !== 401) alert(error.message);   // 401 is handled by the session-expired listener
    });
}

export function listUserCountries() {
    return fetch("/countries", { method: "GET" })
    .then(parseResponse)
    .then(data => {
        const list = document.getElementById("correctGuesses");
        list.innerHTML = "";
        data.forEach(country => {
            const dt = document.createElement("dt");
            dt.textContent = `${country.common_name}`;
            const dd = document.createElement("dd")
            dd.textContent =  `(population: ${country.population.toLocaleString()})`;
            list.appendChild(dt);
            list.appendChild(dd);
        });
    })
    .catch(error => console.error("Error", error));
}


