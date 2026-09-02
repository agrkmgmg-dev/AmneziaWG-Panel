package ir.golidev.amneziawg

import android.content.Context
import android.util.Base64
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.bouncycastle.crypto.params.X25519PrivateKeyParameters

data class DeviceKeys(val privateKey: String, val publicKey: String)

class DeviceKeyStore(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "device_keys",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    fun getOrCreate(): DeviceKeys {
        val existingPrivate = prefs.getString("private", null)
        val existingPublic = prefs.getString("public", null)
        if (existingPrivate != null && existingPublic != null) {
            return DeviceKeys(existingPrivate, existingPublic)
        }
        val privateBytes = ByteArray(32).also { java.security.SecureRandom().nextBytes(it) }
        val privateParams = X25519PrivateKeyParameters(privateBytes, 0)
        val publicBytes = privateParams.generatePublicKey().encoded
        val keys = DeviceKeys(
            Base64.encodeToString(privateBytes, Base64.NO_WRAP),
            Base64.encodeToString(publicBytes, Base64.NO_WRAP),
        )
        prefs.edit().putString("private", keys.privateKey).putString("public", keys.publicKey).apply()
        return keys
    }
}
