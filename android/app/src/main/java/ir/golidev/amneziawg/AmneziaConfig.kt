package ir.golidev.amneziawg

data class ClientConfig(
    val privateKey: String,
    val address: String,
    val endpoint: String,
    val serverPublicKey: String,
    val params: Map<String, String>,
) {
    fun asText(): String = buildString {
        appendLine("[Interface]")
        appendLine("PrivateKey = $privateKey")
        appendLine("Address = $address")
        params.forEach { (key, value) -> appendLine("$key = $value") }
        appendLine()
        appendLine("[Peer]")
        appendLine("PublicKey = $serverPublicKey")
        appendLine("Endpoint = $endpoint")
        appendLine("AllowedIPs = 0.0.0.0/0, ::/0")
        appendLine("PersistentKeepalive = 25")
    }
}

fun DeviceConfig.toClientConfig(privateKey: String) =
    ClientConfig(privateKey, address, endpoint, serverPublicKey, awgParams)
