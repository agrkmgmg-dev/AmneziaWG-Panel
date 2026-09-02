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
import androidx.compose.material3.TextButton
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
    var loggedIn by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val context = androidx.compose.ui.platform.LocalContext.current
    val session = remember { SessionStore(context) }
    var peerId by remember { mutableIntStateOf(session.peerId) }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("GoliDev VPN", style = MaterialTheme.typography.headlineLarge)
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
                            session.token = token
                            val keys = DeviceKeyStore(context).getOrCreate()
                            val config = api.bindDevice(token, keys.publicKey)
                            val profile = config.toClientConfig(keys.privateKey).asText()
                            session.profile = profile
                            session.peerId = config.peerId
                            launch(Dispatchers.Main) {
                                peerId = config.peerId
                                message = "دستگاه ثبت شد؛ پروفایل اختصاصی آماده است"
                                loggedIn = true
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
        if (loggedIn) {
            Text("وضعیت: این گوشی به حساب شما متصل است — شناسه $peerId")
            Text("کلید خصوصی فقط روی همین گوشی نگه‌داری می‌شود.")
            Button(onClick = {
                session.clear()
                loggedIn = false
                peerId = -1
                message = "نشست پاک شد"
            }) {
                Text("خروج از حساب")
            }
        } else if (session.token != null) {
            TextButton(onClick = {
                loggedIn = true
                peerId = session.peerId
                message = "نشست قبلی بازیابی شد"
            }) {
                Text("بازیابی نشست قبلی")
            }
        }
    }
}
