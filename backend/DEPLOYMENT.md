# استقرار پنل GoliDev VPN

پس از قرار دادن این نسخه روی سرور، migration را قبل از restart سرویس اجرا کنید:

```bash
cd /opt/amneziawg-panel
docker compose exec amneziawg-panel alembic -c backend/alembic.ini upgrade head
docker compose up -d --build amneziawg-panel
```

متغیرهای لازم در `.env` کانتینر پنل:

```env
AWG_AUTO_SYNC=true
AWG_PEER_RATE_LIMIT_MBPS=15
```

محدودیت سرعت از طریق سوکت `/run/amneziawg-panel/awg.sock` اعمال می‌شود؛
بنابراین این سوکت باید به کانتینر پنل mount شده باشد و helper میزبان باید
دستورهای `add`، `remove`، `dump` و `rate` را پشتیبانی کند.

هر کاربر یک Peer دارد. هنگام ورود اولین‌بار به اپ اختصاصی، کلید عمومی همان
گوشی ثبت می‌شود و ورود با گوشی دیگری رد خواهد شد.
