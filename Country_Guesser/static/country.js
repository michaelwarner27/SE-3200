// Country data comes from our own server, which holds the restcountries API key
const baseURL = "/api/country/"


class Country{
    constructor(commonName){
        this.commonName = commonName
        // Call fetchPayload() yourself (and await it) once you want the data
    }

    async fetchPayload(){
        // Exact-name route: a substring query would match "Guinea" to "Equatorial Guinea" first
        let search = baseURL + encodeURIComponent(this.commonName)
        const response = await fetch(search)
        if (response.status === 401){
            window.dispatchEvent(new Event("session-expired"))
        }
        this.payload = await response.json().catch(() => null);
        if (!response.ok || !this.payload?.data?.objects?.length){
            return false
        }
        this.parse()
        return true
    }

    parse(){
        const c = this.payload.data.objects[0]
        this.population = c.population
        this.flagHTML = c.flag?.html_entity
        this.flagPNG  = c.flag?.url_png
        // Territories such as Antarctica have empty currencies/capitals/languages, so guard each one
        this.currency = c.currencies?.[0]?.name
        this.areaMiles = c.area?.miles
        this.areaKilometer = c.area?.kilometers
        this.officialName = c.names?.official
        this.capitals = (c.capitals ?? []).map(capital => capital.name)
        this.languages = (c.languages ?? []).map(language => language.name)
        this.currencies = (c.currencies ?? []).map(currency => currency.name)
        this.subregion = c.subregion
        this.governmentType = c.government_type
        this.shortDescription = c.descriptions?.short
        this.memberships = c.memberships ?? {}
        this.classification = c.classification ?? {}
        this.wikipediaURL = c.links?.wikipedia
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
    getCapitals(){
        return this.capitals
    }
    getLanguages(){
        return this.languages
    }
    getCurrencies(){
        return this.currencies
    }
    getSubregion(){
        return this.subregion
    }
    getGovernmentType(){
        return this.governmentType
    }
    getShortDescription(){
        return this.shortDescription
    }
    getMemberships(){
        return this.memberships
    }
    getClassification(){
        return this.classification
    }
    getWikipediaURL(){
        return this.wikipediaURL
    }

}
export default Country