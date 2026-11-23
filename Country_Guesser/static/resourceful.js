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

// Deletes every saved guess for the current user using the existing DELETE /countries/<id> route.
export async function clearUserCountries() {
    try {
        const countries = await fetch("/countries", { method: "GET" }).then(parseResponse);
        await Promise.all(countries.map(country =>
            fetch(`/countries/${country.id}`, { method: "DELETE" }).then(parseResponse)
        ));
    } catch (error) {
        console.error("Error:", error);
        if (error.status !== 401) alert(error.message);
    }
    return listUserCountries();
}

// Stored flags are HTML entity codes (e.g. "&#127464;&#127462;"); decode to plain text without using innerHTML
function decodeEntities(code) {
    return new DOMParser().parseFromString(code ?? "", "text/html").documentElement.textContent;
}

export function listUserCountries() {
    return fetch("/countries", { method: "GET" })
    .then(parseResponse)
    .then(data => {
        const list = document.getElementById("correctGuesses");
        list.innerHTML = "";
        document.getElementById("score").textContent = data.length;
        data.forEach(country => {
            const item = document.createElement("li");
            const flag = document.createElement("span");
            flag.className = "listFlag";
            flag.textContent = decodeEntities(country.html_flag_code);
            const name = document.createElement("span");
            name.className = "listName";
            name.textContent = country.common_name;
            const more = document.createElement("button");
            more.type = "button";
            more.className = "btn btn-ghost moreInfoButton";
            more.textContent = "More info";
            more.addEventListener("click", () => {
                more.textContent = "More info";
                window.dispatchEvent(new CustomEvent("show-more-info", {detail: {commonName: country.common_name, button: more}}));
            });
            item.append(flag, name, more);
            list.appendChild(item);
        });
    })
    .catch(error => console.error("Error", error));
}


