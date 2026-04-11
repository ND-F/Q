// تغيير النسخة لـ v3 لإجبار المتصفح على التحديث
const CACHE_NAME = "museum-cache-v3";

const ASSETS = [
    "/Q/",
    "/Q/index.html",
    "/Q/scan.html",
    "/Q/style.css",
    "/Q/data/artworks.json", // إضافة ملف البيانات
    "/Q/images/no-image.jpg",
    "/Q/images/logo-nadim.png",
    "/Q/images/MIALOGO.png"    // إضافة لوجو المتحف الجديد
];

// 1. تثبيت الـ Service Worker وتحميل الملفات الأساسية
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log("Caching latest assets...");
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting(); // تفعيل فوري بدون انتظار إغلاق المتصفح
});

// 2. تنظيف النسخ القديمة (v1, v2) وتفعيل v3
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        console.log("Deleting old cache:", key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// 3. إدارة الطلبات بذكاء
self.addEventListener("fetch", event => {
    const request = event.request;
    const url = new URL(request.url);

    // أ- سياسة التعامل مع HTML والبيانات (Network First)
    // عشان نضمن إن المستخدم يشوف أحدث كود وأحدث بيانات لو فيه نت
    if (request.headers.get("accept").includes("text/html") || url.pathname.includes("artworks.json")) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // تحديث الكاش بالنسخة الجديدة اللي جت من النت
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, response.clone());
                        return response;
                    });
                })
                .catch(() => {
                    // لو مفيش نت، طلع اللي متخزن في الكاش
                    return caches.match(request);
                })
        );
        return;
    }

    // ب- سياسة الصور والملفات الثابتة (Cache First)
    // الصور مش بتتغير كتير، فنجيبها من الكاش أسرع
    event.respondWith(
        caches.match(request).then(cachedResponse => {
            if (cachedResponse) return cachedResponse;

            return fetch(request).then(networkResponse => {
                return caches.open(CACHE_NAME).then(cache => {
                    cache.put(request, networkResponse.clone());
                    return networkResponse;
                });
            });
        })
    );
});
