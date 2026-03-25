const CACHE="museum-cache";

self.addEventListener("install",e=>{
e.waitUntil(
caches.open(CACHE).then(cache=>{
return cache.addAll([
"/Q/",
"/Q/index.html",
"/Q/scan.html",
"/Q/style.css",
"/Q/images/no-image.jpg"
]);
})
);
});

self.addEventListener("fetch",e=>{
e.respondWith(
caches.match(e.request).then(res=>{
return res || fetch(e.request);
})
);
});
