# NADIM in Museum of Islamic Arts - Digital Exhibition v3.0

تطبيق ويب تفاعلي مصمم لتعزيز تجربة زوار متحف الفن الإسلامي، يربط بين القطع الأثرية ومحتوى رقمي غني من خلال نظام أكواد QR ذكي.

## 🚀 ما الجديد في الإصدار 3.0 (v3.0 Highlights)

تم تحديث المشروع بالكامل لتحسين الأداء وتجربة المستخدم، وتشمل الميزات الجديدة:

* **Smart Swapping & Navigation:** نظام تقليب ذكي بين صور القطعة الواحدة بالسحب (Swipe) وبين القطع المختلفة (Next/Prev) بدون إعادة تحميل الصفحة.
* **Advanced Hybrid Zoom:** زووم طبيعي (Pinch-to-zoom) فائق السلاسة للموبايل، وزووم دقيق بنقطة الماوس لنسخة الديسكتوب.
* **Theme Persistence:** نظام ذكي لحفظ اختيار المستخدم بين الثيم الفاتح (Light) والغامق (Dark) ومزامنته عبر جميع صفحات الموقع.
* **HQ QR Code System:** مولد أكواد QR مخصص بجودة عالية (SVG) مع دمج الهوية البصرية للمؤسسة (اللوجو والألوان الرسمية).
* **Optimized Service Worker:** تحسين نظام الكاش (PWA) لضمان سرعة التحميل ودعم العمل في ظروف الإنترنت الضعيفة داخل المتحف.
* **Clean Data Architecture:** الاعتماد على ملف JSON محلي بدلاً من الطلبات الخارجية لضمان سرعة استجابة فائقة.

## 🎨 الهوية البصرية (Visual Identity)

يعتمد المشروع على لوحة ألوان رسمية تعكس عراقة وفخامة المحتوى:
* **Dark Green:** `#06444C` (الأخضر الداكن الأساسي)
* **Dark Red:** `#4A121C` (الأحمر الداكن للتباين)
* **Gold:** `#E1A93E` (الذهبي للعناوين)
* **Creamy:** `#EAE8D8` (الكريمي للخلفيات المريحة)
* **Light Green:** `#ADCAC9` (الأخضر الفاتح للمسات العصرية)

## 🛠 التقنيات المستخدمة (Tech Stack)

* **Frontend:** HTML5, CSS3 (Custom Properties & Grid Areas), JavaScript (ES6+).
* **Data:** JSON-based local database.
* **Libraries:** QRCodeStyling (for HQ SVG generation).
* **PWA:** Service Workers for offline caching and performance.

## 📂 هيكل الملفات (File Structure)

* `index.html`: البوابة الرئيسية والمعرض الشامل.
* `scan.html`: العارض الذكي للقطع الأثرية (قلب المشروع).
* `qr.html`: مصنع أكواد QR الرسمية بجودة الطباعة.
* `style.css`: ملف التنسيق الموحد للهوية البصرية.
* `sw.js`: مدير الكاش والعمل بدون إنترنت.
* `data/artworks.json`: قاعدة بيانات القطع والصور والوصف.

---
© 2024 Nadim Foundation. All Rights Reserved.
Designed for the Museum of Islamic Arts.
