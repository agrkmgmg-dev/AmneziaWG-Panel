package ir.golidev.amneziawg

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SessionStore(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "session",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    var token: String?
        get() = prefs.getString("access_token", null)
        set(value) = prefs.edit().putString("access_token", value).apply()

    var profile: String?
        get() = prefs.getString("profile", null)
        set(value) = prefs.edit().putString("profile", value).apply()

    var peerId: Int
        get() = prefs.getInt("peer_id", -1)
        set(value) = prefs.edit().putInt("peer_id", value).apply()

    fun clear() = prefs.edit().clear().apply()
}
