# AmneziaWG Android Client

نسخه‌ی اولیه‌ی اپ اختصاصی Android برای پنل `golidev.ir`.

## وضعیت فعلی

- اسکلت Native Android با Kotlin و Jetpack Compose
- صفحه‌ی ورود اولیه
- مجوز شبکه و وابستگی‌های لازم برای API
- آماده برای اضافه‌شدن ثبت دستگاه و اتصال VPN

## ساخت APK

این پروژه به Android SDK 35 و JDK 17 نیاز دارد:

```bash
./gradlew assembleDebug
```

اتصال واقعی AmneziaWG و ثبت کلید دستگاه بعد از آماده‌شدن endpointهای Device Binding پنل اضافه می‌شود.
