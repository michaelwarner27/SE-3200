function createCountry() {
    const countryData = {
        common_name: document.getElementById("name").value,
        official_name: document.getElementById("official_name").value,
        population: parseInt(document.getElementById("population").value),
        html_flag_code: document.getElementById("flagCode").value,
        area: parseInt(document.getElementById("Area").value)
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
        document.getElementById("countryForm").reset();
        return listCountries();
    })
    .catch(error => {
        console.error("Error:", error);
        alert(error.message);
    });
}

function listCountries() {
    return fetch("/countries", { method: "GET" })
    .then(response => response.json().then(data => {
        if (!response.ok) throw new Error(data.error || response.statusText);
        return data;
    }))
    .then(data => {
        const list = document.getElementById("countryList");
        list.innerHTML = "";
        data.forEach(country => {
            const li = document.createElement("li");
            li.textContent = `${country.common_name} (population: ${country.population.toLocaleString()})`;
            list.appendChild(li);
        });
    })
    .catch(error => console.error("Error", error));
}

const form = document.getElementById("countryForm");
form.addEventListener("submit", function (event) {
    event.preventDefault();
    createCountry();
});

listCountries();
