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
    .then(response => response.json().then(data => {
        if (!response.ok) throw new Error(data.error || response.statusText);
        return data;
    }))
    .then(data => {
        console.log("Country created:", data);
        document.getElementById("form").reset();
        // return listUserCountries();
    })
    .catch(error => {
        console.error("Error:", error);
        alert(error.message);
    });
}

export function listUserCountries() {
    return fetch("/countries", { method: "GET" })
    .then(response => response.json().then(data => {
        if (!response.ok) throw new Error(data.error || response.statusText);
        return data;
    }))
    .then(data => {
        const list = document.getElementById("correctGuesses");
        list.innerHTML = "";
        data.forEach(country => {
            const li = document.createElement("li");
            li.textContent = `${country.common_name} (population: ${country.population.toLocaleString()})`;
            list.appendChild(li);
        });
    })
    .catch(error => console.error("Error", error));
}

// export {storeUserCountry, listUserCountries};

