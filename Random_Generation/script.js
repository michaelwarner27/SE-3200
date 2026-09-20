const commonNames = ['Abkhazia', 'Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island', 'Brazil', 'British Indian Ocean Territory', 'British Virgin Islands', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Caribbean Netherlands', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czechia', 'DRC', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern and Antarctic Lands', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands', 'Honduras', 'Hong Kong'];
const APIKEY = "bearer rc_live_dda8f02bea1b422a9bc24dbaba0c63bb"
const urlapi = 'https://api.restcountries.com/countries/v5?response_fields=names.common'
const baseURL = "https://api.restcountries.com/countries/v5?"
let currentCountry = "example"
let payload = ""
let population = 0
let currencies = []
let moneyString = ""
let Flag = "&#127465;&#127472;"
let landAreaMiles = 0
// let exampleCountry = "Denmark"
// let examplePopulation = 6032304
// let exampleCurrency = "Danish krone"
// let exampleFlag = "https://flags.restcountries.com/v5/w640/dk.png"
// async function Names() {
//   const url = 'https://api.restcountries.com/countries/v5?limit=100&response_fields=names.common';
//   const response = await fetch(url, {
//     method: 'GET',
//     headers: {
//       'Authorization': APIKEY
//     }
//   });
//   const payload = await response.json();
//   const countryNames = payload.data.objects.map(country => country.names.common);
//   console.log(countryNames);
//   return countryNames;
// }

function Start(){
    currentCountry = commonNames[ Math.ceil(Math.random() * commonNames.length)]
    getCountryData(currentCountry)
}

async function getCountryData(country){
    search = baseURL + "names.common=" + country
    const response = await fetch(search, {
        method: 'GET',
    headers: {
        'Authorization': APIKEY
    }
    });
    payload = await response.json();
    console.log("payload")
    console.log(payload)
    population = grabPopulation(payload)
    flag = grabFlagHTML(payload)
    // money = grabCurrencies(payload)
    areaMiles = grabLandAreaMiles(payload)
}

function grabPopulation(payload){
    population = payload.data.objects.map(country => country.population) 
    document.getElementById("Population").innerHTML = population + " People"
    console.log(population)
    return population
}

function grabFlagHTML(payload){
    flag = payload.data.objects.map(country => country.flag.html_entity) 
    document.getElementById("FlagHTML").innerHTML = flag[0]
    // console.log(flag)
    return flag
}
function grabFlagImage(payload){
    flag = payload.data.objects.map(country => country.flag.url_png) 
    document.getElementById("Flag").src = flag
    // console.log(flag)
    return flag
}

function grabCurrencies(payload){
    let moneyList = payload.data.objects.map(country => country.currencies) 
    // console.log(moneyList)
    
    moneyList.forEach(element => {
        moneyString += element[0].name + "\n"
    });
    document.getElementById("money").innerHTML = moneyString

    return moneyString
}

function grabLandAreaMiles(payload){
    landAreaMiles = payload.data.objects.map(country => country.area.miles) 
    document.getElementById("landAreaMiles").innerHTML = landAreaMiles + " Square Miles"
    console.log(landAreaMiles)
    return landAreaMiles
}

function Cheat(){
    document.getElementById("cheat").innerHTML = "This nation is " + currentCountry
}
function DisplayMoreInfo(){
    document.getElementById("infoCountryName").innerHTML = currentCountry
    grabFlagImage(payload)
    document.getElementById("info").innerHTML = "Population: " + population + "<br> Land Area in Miles: " + landAreaMiles


}

let guessBox = document.getElementById("guess")

function SubmitGuess() {
    userGuess = guessBox.value
    if (userGuess == currentCountry){
        // alert("Correct!")
        let correctGuessDisplay = "<dt>"+currentCountry + " <span id=\"FlagHTML\">" + Flag + "</span></dt><dd>Population: " + population + "</dd>"
        // console.log(correctGuessDisplay)
        document.getElementById("correctGuesses").insertAdjacentHTML("afterend", correctGuessDisplay)
        Start()
        DisplayMoreInfo()
    }else{
        alert("Wrong! Try again")
    }
    
}