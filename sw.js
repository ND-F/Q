const CACHE_NAME = "museum-cache-v2";

const ASSETS = [
"/Q/",
"/Q/index.html",
"/Q/style.css",
"/Q/images/no-image.jpg"
];


// تثبيت الـ Service Worker
self.addEventListener("install", event => {

event.waitUntil(
caches.open(CACHE_NAME).then(cache=>{
return cache.addAll(ASSETS);
})
);

self.skipWaiting();

});


// تفعيل النسخة الجديدة وحذف القديمة
self.addEventListener("activate", event => {

event.waitUntil(

caches.keys().then(keys=>{
return Promise.all(
keys.map(key=>{
if(key !== CACHE_NAME){
return caches.delete(key);
}
})
);
})

);

self.clients.claim();

});


// إدارة الطلبات
self.addEventListener("fetch", event => {

const request = event.request;


// لا تخزن HTML حتى لا تظهر نسخة قديمة
if(request.headers.get("accept").includes("text/html")){

event.respondWith(
fetch(request).catch(()=>{
return caches.match("/Q/index.html");
})
);

return;

}


// الصور و CSS و JS يتم تخزينهم
event.respondWith(

caches.match(request).then(cached=>{
return cached || fetch(request).then(response=>{

return caches.open(CACHE_NAME).then(cache=>{
cache.put(request,response.clone());
return response;
});

});

})

);

});