package ir.golidev.amneziawg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    LoginScreen()
                }
            }
        }
    }
}

@Composable
private fun LoginScreen() {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var message by remember { mutableStateOf("ورود برای اتصال امن") }
    val scope = rememberCoroutineScope()
    val context = androidx.compose.ui.platform.LocalContext.current

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("AmneziaWG", style = MaterialTheme.typography.headlineLarge)
        Text(message)
        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("نام کاربری") },
            singleLine = true,
        )
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("رمز عبور") },
            visualTransformation = PasswordVisualTransformation(),
            singleLine = true,
        )
        Button(
            onClick = {
                if (username.isBlank() || password.isBlank()) {
                    message = "نام کاربری و رمز عبور را وارد کنید"
                } else {
                    message = "در حال ثبت دستگاه..."
                    scope.launch(Dispatchers.IO) {
                        try {
                            val api = ApiClient()
                            val token = api.login(username, password)
                            val keys = DeviceKeyStore(context).getOrCreate()
                            val config = api.bindDevice(token, keys.publicKey)
                            val profile = config.toClientConfig(keys.privateKey).asText()
                            launch(Dispatchers.Main) {
                                message = "دستگاه ثبت شد؛ پروفایل Peer #${config.peerId} آماده است (${profile.length} بایت)"
                            }
                        } catch (error: Exception) {
                            launch(Dispatchers.Main) {
                                message = error.message ?: "خطا در ثبت دستگاه"
                            }
                        }
                    }
                }
            },
        ) {
            Text("ورود")
        }
    }
}
