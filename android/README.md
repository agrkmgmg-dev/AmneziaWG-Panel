# AmneziaWG Android Client

نسخه‌ی اولیه‌ی اپ اختصاصی Android برای پنل `golidev.ir`.

## وضعیت فعلی

- اسکلت Native Android با Kotlin و Jetpack Compose
- صفحه‌ی ورود اولیه
- ورود به API پنل و ثبت کلید عمومی دستگاه
- نگهداری رمزنگاری‌شده‌ی کلید دستگاه
- تولید پروفایل کامل AmneziaWG از کلید غیرقابل‌خروجی
- اسکلت سرویس VPN اندروید

سرویس VPN عمداً تا زمان اضافه‌شدن موتور Native AmneziaWG تونل جعلی ایجاد نمی‌کند.

## ساخت APK

این پروژه به Android SDK 35 و JDK 17 نیاز دارد:

```bash
./gradlew assembleDebug
```

همچنین Workflow گیت‌هاب با هر Push روی `main`، فایل `app-debug.apk` را
به‌صورت Artifact می‌سازد. برای اجرای دستی از تب Actions، گزینه‌ی **Build
Android APK** و سپس **Run workflow** را انتخاب کنید.

اتصال واقعی AmneziaWG و ثبت کلید دستگاه بعد از آماده‌شدن endpointهای Device Binding پنل اضافه می‌شود.
