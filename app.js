/* app.js - النسخة المحدثة (Smart Slideshow Mode)
   متوافق مع MIA Project 2024
*/

const DATA_PATH = "data/artworks.json";
let artworks = [];
let currentIndex = 0;
let imageIndex = 0;
let slideInterval;

// 1. تحميل البيانات من الملف المحلي (أسرع بـ 10 أضعاف من الـ API)
fetch(DATA_PATH + "?v=" + new Date().getTime())
    .then(res => res.json())
    .then(data => {
        // ترتيب القطع حسب الـ order لو موجود
        artworks = data.sort((a, b) => Number(a.order || 0) - Number(b.order || 0));

        if (artworks.length > 0) {
            // التحقق من وجود ID في الرابط أولاً
            const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            const foundIndex = artworks.findIndex(a => a.id === id);
            
            loadArtwork(foundIndex !== -1 ? foundIndex : 0);
        }
    })
    .catch(err => console.error("فشل تحميل البيانات في app.js:", err));

// 2. تحميل بيانات القطعة
function loadArtwork(index) {
    currentIndex = index;
    imageIndex = 0;
    const art = artworks[index];
    if (!art) return;

    // دعم اللغتين في العرض
    const titleEn = art.title_en || "";
    const titleAr = art.title_ar || "";
    
    // تحديث النصوص في الصفحة (تأكد أن الـ IDs دي موجودة في الـ HTML بتاعك)
    if(document.getElementById("title")) 
        document.getElementById("title").innerText = `${titleAr} / ${titleEn}`;
    
    if(document.getElementById("id")) document.getElementById("id").innerText = art.id || "";
    
    // استخدام الخامات الجديدة (عربي/انجليزي)
    if(document.getElementById("material")) 
        document.getElementById("material").innerText = art.material_ar || art.material_en || "";

    if(document.getElementById("desc")) 
        document.getElementById("desc").innerText = art.desc_ar || art.desc_en || "";

    showImage();
    startAutoSlide(); // إعادة تشغيل التقليب التلقائي
}

// 3. عرض الصور (دعم حتى 5 صور مع تنظيف الصور المكسورة)
function showImage() {
    const art = artworks[currentIndex];
    // تجميع الصور المتاحة فقط
    const availableImages = [art.image1, art.image2, art.image3, art.image4, art.image5].filter(img => img && img.trim() !== "");
    
    if (imageIndex >= availableImages.length) imageIndex = 0;
    
    const imgElement = document.getElementById("img");
    if (imgElement && availableImages[imageIndex]) {
        imgElement.src = availableImages[imageIndex];
        imgElement.onerror = () => { imgElement.src = "images/no-image.jpg"; };
    }
}

// 4. التحكم (التالي والسابق)
function next() {
    currentIndex = (currentIndex + 1) % artworks.length;
    loadArtwork(currentIndex);
}

function prev() {
    currentIndex = (currentIndex - 1 + artworks.length) % artworks.length;
    loadArtwork(currentIndex);
}

// 5. التقليب التلقائي الذكي (Smart Slideshow)
function startAutoSlide() {
    clearInterval(slideInterval);
    slideInterval = setInterval(() => {
        const art = artworks[currentIndex];
        const availableImages = [art.image1, art.image2, art.image3, art.image4, art.image5].filter(img => img && img.trim() !== "");
        
        if (availableImages.length > 1) {
            imageIndex = (imageIndex + 1) % availableImages.length;
            showImage();
        }
    }, 5000); // تقليب كل 5 ثواني
}

// مزامنة الثيم من الـ LocalStorage
if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light");
}
