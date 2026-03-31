const API =
"https://script.google.com/macros/s/AKfycbxW__sGqYA7pI4KQFKrwSaV4eQ-p6YrTcAwoc8ORZLyl9NOdF1r2Y983_gGhpbkkdLv/exec";

let artworks = [];
let currentIndex = 0;
let imageIndex = 0;

fetch(API)
.then(res => res.json())
.then(data => {

artworks = data.sort((a,b)=>Number(a.order)-Number(b.order));

if(artworks.length > 0){
loadArtwork(0);
}

});

function loadArtwork(index){

currentIndex = index;
imageIndex = 0;

const art = artworks[index];

document.getElementById("title").innerText =
(art.title_en || "") + " / " + (art.title_ar || "");

document.getElementById("id").innerText = art.id || "";
document.getElementById("date").innerText = art.date || "";
document.getElementById("material").innerText = art.material || "";

document.getElementById("height").innerText =
art.height ? art.height + " cm" : "";

document.getElementById("width").innerText =
art.width ? art.width + " cm" : "";

document.getElementById("desc").innerText =
(art.desc_en || "") + " - " + (art.desc_ar || "");

showImage();

}

function showImage(){

const art = artworks[currentIndex];

let imgPath;

if(imageIndex === 0){
imgPath = art.image1;
}else{
imgPath = art.image2 || art.image1;
}

const img = document.getElementById("img");

img.onerror = function(){
img.src = "images/no-image.jpg";
};

img.src = imgPath;

}

function next(){

currentIndex++;

if(currentIndex >= artworks.length)
currentIndex = 0;

loadArtwork(currentIndex);

}

function prev(){

currentIndex--;

if(currentIndex < 0)
currentIndex = artworks.length - 1;

loadArtwork(currentIndex);

}

setInterval(()=>{

const art = artworks[currentIndex];

if(!art.image2) return;

imageIndex++;

if(imageIndex > 1) imageIndex = 0;

showImage();

},6000);