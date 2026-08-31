package ir.golidev.amneziawg

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

data class DeviceConfig(
    val peerId: Int,
    val address: String,
    val endpoint: String,
    val serverPublicKey: String,
    val awgParams: Map<String, String>,
)

class ApiClient(
    private val baseUrl: String = "https://golidev.ir",
    private val http: OkHttpClient = OkHttpClient(),
) {
    private val jsonType = "application/json".toMediaType()

    fun login(username: String, password: String): String {
        val body = JSONObject()
            .put("username", username)
            .put("password", password)
            .toString()
            .toRequestBody(jsonType)
        val request = Request.Builder()
            .url("$baseUrl/api/v1/auth/login")
            .post(body)
            .build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("ورود ناموفق بود")
            return JSONObject(response.body!!.string()).getString("access_token")
        }
    }

    fun bindDevice(token: String, publicKey: String): DeviceConfig {
        val body = JSONObject().put("public_key", publicKey)
            .toString().toRequestBody(jsonType)
        val request = Request.Builder()
            .url("$baseUrl/api/v1/devices/bind")
            .header("Authorization", "Bearer $token")
            .post(body)
            .build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error(response.body?.string() ?: "ثبت دستگاه ناموفق بود")
            val obj = JSONObject(response.body!!.string())
            val params = mutableMapOf<String, String>()
            val rawParams = obj.getJSONObject("awg_params")
            rawParams.keys().forEach { key -> params[key] = rawParams.getString(key) }
            return DeviceConfig(
                peerId = obj.getInt("peer_id"),
                address = obj.getString("address"),
                endpoint = obj.getString("endpoint"),
                serverPublicKey = obj.getString("server_public_key"),
                awgParams = params,
            )
        }
    }
}
