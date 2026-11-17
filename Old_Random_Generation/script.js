const APIKEY = "bearer rc_live_dda8f02bea1b422a9bc24dbaba0c63bb"
const urlapi = 'https://api.restcountries.com/countries/v5?q=canada'
// Access-Control-Allow-Methods(get) 
// Fires a real request against the demo API key.
// Click the button below to run it. The response opens in the Explorer panel.
async function name() {
    const response = await fetch( urlapi, { headers: { 'Authorization': "bearer rc_live_dda8f02bea1b422a9bc24dbaba0c63bb" } });
    const result = await response.json();
    console.log(result)
    
} 
