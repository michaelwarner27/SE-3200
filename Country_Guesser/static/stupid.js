import Country from "./country.js" 
import {storeUserCountry, listUserCountries, clearUserCountries} from "./resourceful.js"
import { register, login, logout, getCurrentUser } from "./auth.js"


// Country-name lists are generated once by tools/build_country_lists.py into static/data/countries/
const LIST_DIR = "/static/data/countries/"
const LIST_KEY = "countryList"
const listCache = new Map()
let countryNames = []

async function loadList(id){
    if (!listCache.has(id)){
        const response = await fetch(`${LIST_DIR}${id}.json`)
        if (!response.ok) throw new Error(`Could not load the "${id}" country list`)
        listCache.set(id, await response.json())
    }
    countryNames = listCache.get(id)
}

async function setupListSelect(){
    const select = document.getElementById("listSelect")
    try{
        const lists = await (await fetch(`${LIST_DIR}index.json`)).json()
        select.innerHTML = ""
        lists.forEach(list => select.add(new Option(`${list.label} (${list.count})`, list.id)))
        let saved = null
        try { saved = localStorage.getItem(LIST_KEY) } catch {}
        select.value = lists.some(list => list.id === saved) ? saved : lists[0].id
        await loadList(select.value)
    } catch (error){
        setGuessMessage(error.message)
    }
}

let currentCountry = new Country()
async function Start(){
    currentCountry = new Country(countryNames[Math.floor(Math.random() * countryNames.length)]) 
    if (!await currentCountry.fetchPayload()){
        currentCountry = new Country()
        setGuessMessage("Couldn't load a country. Press Start again.")
        return
    }
    setGuessMessage("")
    setHint()
}

function setHint(){
    document.getElementById("Population").innerHTML = currentCountry.getPopulation() + " People"
    document.getElementById("FlagHTML").innerHTML = currentCountry.getFlagHTML()
    document.getElementById("landAreaMiles").innerHTML = currentCountry.getLandAreaMiles() + " Square Miles"

}

function Cheat(){
    if (!currentCountry.getCommonName()){
        document.getElementById("cheat").innerHTML = "Click Start!"
    }else{
        document.getElementById("cheat").innerHTML = "This nation is " + currentCountry.getCommonName()

    }
}

const MEMBERSHIP_LABELS = {
    african_union: "African Union", arab_league: "Arab League", asean: "ASEAN", brics: "BRICS",
    commonwealth: "Commonwealth", eu: "EU", eurozone: "Eurozone", g20: "G20", g7: "G7",
    nato: "NATO", oecd: "OECD", opec: "OPEC", schengen: "Schengen", un: "UN"
}

function setBadges(id, labels){
    const container = document.getElementById(id)
    container.replaceChildren()
    if (labels.length === 0){
        container.textContent = "None"
        return
    }
    labels.forEach(label => {
        const badge = document.createElement("span")
        badge.className = "badge"
        badge.textContent = label
        container.appendChild(badge)
    })
}

function countryStatus(c){
    const status = []
    status.push(c.sovereign ? "Sovereign state" : "Not sovereign")
    if (c.dependency) status.push(c.dependency_type ? `Dependency (${c.dependency_type})` : "Dependency")
    if (c.disputed) status.push("Disputed")
    if (c.un_member) status.push("UN member")
    if (c.un_observer) status.push("UN observer")
    return status
}

function DisplayMoreInfo(country = currentCountry){
    const list = (items) => items && items.length ? items.join(", ") : "—"
    const text = (id, value) => document.getElementById(id).textContent = value || "—"

    document.getElementById("infoCountryName").textContent = country.getCommonName()
    document.getElementById("Flag").src = country.getFlagPNG()
    text("infoDescription", country.getShortDescription())
    text("infoCapital", list(country.getCapitals()))
    text("infoLanguages", list(country.getLanguages()))
    text("infoCurrency", list(country.getCurrencies()))
    text("infoSubregion", country.getSubregion())
    text("infoGovernment", country.getGovernmentType())
    setBadges("infoStatus", countryStatus(country.getClassification()))
    setBadges("infoMemberships", Object.entries(country.getMemberships())
        .filter(([, member]) => member)
        .map(([key]) => MEMBERSHIP_LABELS[key] ?? key))

    const wiki = document.getElementById("infoWiki")
    const url = country.getWikipediaURL()
    wiki.hidden = !(url && url.startsWith("https://"))
    if (!wiki.hidden) wiki.href = url
}

function SubmitGuess() {
    if (!currentCountry.getCommonName()){
        return
    }
    let userGuess = document.getElementById("guess").value
    if (userGuess.trim().toLowerCase() == currentCountry.getCommonName().toLowerCase()){
        setGuessMessage("")
        document.getElementById("cheat").textContent = ""
        // createUserCountry()
        correctGuess()
        DisplayMoreInfo()
        Start()
    }else{
        setGuessMessage("Wrong! Try again")
    }
    
}

async function correctGuess(){
    // listUserCountries()
    await storeUserCountry(currentCountry)
    listUserCountries()
    // let correctGuessDisplay =  `<dt> ${currentCountry.getCommonName()} <span id=\"FlagHTML\"${currentCountry.getFlagHTML()}</span></dt><dd>Population: ${currentCountry.getPopulation()} </dd>`
    // document.getElementById("correctGuesses").insertAdjacentHTML("afterend", correctGuessDisplay)

}

function showLoggedIn(user){
    document.getElementById("authDiv").hidden = true;
    document.getElementById("userBar").hidden = false;
    document.getElementById("welcome").textContent = `Welcome, ${user.first_name}!`
    
    document.getElementById("guessDiv").hidden = false;
    document.getElementById("correctDiv").hidden = false;
    document.getElementById("moreInfoDiv").hidden = false;
    listUserCountries()
    
}

function showLoggedOut(){
    document.getElementById("correctGuesses").innerHTML = ""
    document.getElementById("score").textContent = "0"
    document.getElementById("authDiv").hidden = false;
    document.getElementById("userBar").hidden = true;
    document.getElementById("guessDiv").hidden = true;
    document.getElementById("correctDiv").hidden = true;
    document.getElementById("moreInfoDiv").hidden = true;
}

function setGuessMessage(text){
    document.getElementById("guessMessage").textContent = text
}

function setAuthMessage(text){
    document.getElementById("authMessage").textContent = text
}


document.getElementById("start").addEventListener("click", Start)
document.getElementById("listSelect").addEventListener("change", async (event) => {
    try { localStorage.setItem(LIST_KEY, event.target.value) } catch {}
    try{
        await loadList(event.target.value)
        setGuessMessage("")
        Start()
    } catch (error){
        setGuessMessage(error.message)
    }
})
setupListSelect()
document.getElementById("cheatButton").addEventListener("click", Cheat)
document.getElementById("restartButton").addEventListener("click", async () => {
    if (!confirm("Restart? This permanently deletes all of your correct guesses.")) return
    await clearUserCountries()
})

const form = document.getElementById('form');
form.addEventListener("submit", function(event){
    event.preventDefault()
    SubmitGuess()
    document.getElementById('guess').value = ""
})

document.getElementById("registerForm").addEventListener("submit", async(event) => {
    event.preventDefault()
    try{
        await register({
            first_name: document.getElementById("regFirst").value,
            last_name: document.getElementById("regLast").value,
            email: document.getElementById("regEmail").value,
            password: document.getElementById("regPassword").value,
        })
        event.target.reset()
        setAuthMessage("Registration successful! You can now log in.")
    } catch (error) {
        setAuthMessage(error.message)
    }
})

document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault()
    try{
        const user = await login(
            document.getElementById("loginEmail").value,
            document.getElementById("loginPassword").value
        )
        event.target.reset()
        setAuthMessage("")
        showLoggedIn(user)
    } catch (error){
        setAuthMessage(error.message)
    }
})

document.getElementById("logoutButton").addEventListener("click", async() => {
    await logout()
    showLoggedOut()
})

// resourceful.js fires this when /countries answers 401 (e.g. the server restarted and lost the session)
// resourceful.js fires this when a "More info" button is clicked in the correct guesses list
window.addEventListener("show-more-info", async (event) => {
    const button = event.detail.button
    button.disabled = true
    try{
        const country = new Country(event.detail.commonName)
        if (!await country.fetchPayload()) throw new Error("No data found")
        DisplayMoreInfo(country)
        document.getElementById("moreInfoDiv").scrollIntoView({behavior: "smooth", block: "nearest"})
    } catch (error){
        console.error(error)
        button.textContent = "Failed, retry"
    } finally{
        button.disabled = false
    }
})

window.addEventListener("session-expired", () => {
    setAuthMessage("Your session has expired. Please log in again.")
    showLoggedOut()
})

getCurrentUser().then(showLoggedIn).catch(showLoggedOut)
