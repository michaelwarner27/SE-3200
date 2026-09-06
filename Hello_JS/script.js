const gifs = ["Aerial_Drop.gif", "WakeSurfCrash.gif", "ClimbingFall.gif"];
let gif_index = 0;
console.log(gifs);
let changeImage = () =>{
    console.log("Gif switch");
    gif_index ++;
    if (gif_index >= gifs.length){
        gif_index = 0;
    }
    document.getElementById("gif").src = gifs[gif_index];
}
