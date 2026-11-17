import Country from "./country.js" 
import "./resourceful.js"
//ToDo: add the rest of the country names
const commonNames = ['Abkhazia', 'Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island', 'Brazil', 'British Indian Ocean Territory', 'British Virgin Islands', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Caribbean Netherlands', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czechia', 'DRC', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern and Antarctic Lands', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands', 'Honduras', 'Hong Kong'];
let currentCountry = new Country("example")
async function Start(){
    currentCountry = new Country(commonNames[Math.ceil(Math.random() * commonNames.length)]) 
    await currentCountry.fetchPayload()
    if (! currentCountry){
        // Do error thing
    }
    console.log(currentCountry)
    console.log(currentCountry.getCommonName())
    setHint()
}

function setHint(){
    document.getElementById("Population").innerHTML = currentCountry.getPopulation() + " People"
    document.getElementById("FlagHTML").innerHTML = currentCountry.getFlagHTML()
    document.getElementById("landAreaMiles").innerHTML = currentCountry.getLandAreaMiles() + " Square Miles"

}

function Cheat(){
    document.getElementById("cheat").innerHTML = "This nation is " + currentCountry.getCommonName()
}

function DisplayMoreInfo(){
    document.getElementById("infoCountryName").innerHTML = currentCountry.getCommonName()
    document.getElementById("info").innerHTML = `Population: ${currentCountry.getPopulation()} <br> Land Area in Miles: ${currentCountry.getLandAreaMiles()}`
    document.getElementById("Flag").src = currentCountry.getFlagPNG()
}

function SubmitGuess() {
    let userGuess = document.getElementById("guess").value
    if (userGuess.trim().toLowerCase() == currentCountry.getCommonName().toLowerCase()){
        // createUserCountry()
        UserAnswers()
        DisplayMoreInfo()
        Start()
    }else{
        alert("Wrong! Try again")
    }
    
}
function UserAnswers(){
    // listUserCountries()
    let correctGuessDisplay =  `<dt> ${currentCountry.getCommonName()} <span id=\"FlagHTML\"${currentCountry.getFlagHTML()}</span></dt><dd>Population: ${currentCountry.getPopulation()} </dd>`
    document.getElementById("correctGuesses").insertAdjacentHTML("afterend", correctGuessDisplay)

}

document.getElementById("start").addEventListener("click", Start)
document.getElementById("cheatButton").addEventListener("click", Cheat)

const form = document.getElementById('form');
form.addEventListener("submit", function(event){
    event.preventDefault()
    console.log("no refresh")
    SubmitGuess()
    document.getElementById('guess').value = ""
})