async function loadMessages(){
    let response = await fetch('/messages')
    // response.then(response.json())
    let list = await response.json()
    // let list = JSON.parse(json)
    let html = ""
    for (const value of list){
        html += "<li>"+ value + "</li>"
    }
    // console.log(html)
    document.getElementById("messages").innerHTML = html
}

async function postMessage(){
    let mess = new URLSearchParams({message: document.getElementById("message").value})
    let response = await fetch('/messages', {method: 'POST', body: mess})
    console.log(response)
    if( response.status === 201){
        document.getElementById("message").value = ""
        await loadMessages()
    }
}

document.getElementById("form").addEventListener("submit", async (e) => {e.preventDefault(); await postMessage();})

loadMessages()