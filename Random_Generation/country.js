const APIKEY = "bearer rc_live_dda8f02bea1b422a9bc24dbaba0c63bb"
const baseURL = "https://api.restcountries.com/countries/v5?"


class Country{
    constructor(commonName){
        this.commonName = commonName
        if (commonName == "example"){
            return
        }
        console.log(this.commonName)
        this.fetchPayload()
    }

    async fetchPayload(){
        let search = baseURL + "names.common=" + this.commonName
        const response = await fetch(search, {
            method: 'GET',
        headers: {
            'Authorization': APIKEY
        }
        });
        this.payload = await response.json();
        console.log(this.payload)
        this.parse()
        if (!this.payload){
            return false
            // console.error("No payload");
            // exit()
        }
        
        return true
    }

    parse(){
        this.population = this.payload.data.objects.map(country => country.population)[0]
        this.flagHTML = this.payload.data.objects.map(country => country.flag.html_entity) [0]
        this.flagPNG  = this.payload.data.objects.map(country => country.flag.url_png)[0]
        this.currency = this.payload.data.objects.map(country => country.currencies)[0].name
        this.areaMiles = this.payload.data.objects.map(country => country.area.miles) [0]
        this.areaKilometer = this.payload.data.objects.map(country => country.area.kilometer)
        this.officialName = this.payload.data.objects.map(country => country.names.official) 
        this.capital = this.payload.data.objects.map(country => country.capital)[0] 
    }

    getCommonName(){
        return this.commonName
    }
    
    getOfficialName(){
        return this.officialName
    }
    getPopulation(){
        return this.population
    }
    getFlagHTML(){
        return this.flagHTML
    }
    getFlagPNG(){
        return this.flagPNG
    }
    getLandAreaMiles(){
        return this.areaMiles
    }
    getLandAreaKilometers(){
        return this.areaKilometer
    }
    getCurrency(){
        return this.currency
    }

}
export default Country