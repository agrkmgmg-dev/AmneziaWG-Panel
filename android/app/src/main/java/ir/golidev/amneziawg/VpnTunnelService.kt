package ir.golidev.amneziawg

import android.content.Intent
import android.net.VpnService
import android.os.IBinder

/**
 * Lifecycle placeholder for the native AmneziaWG engine.
 *
 * The service deliberately does not claim a tunnel until the native engine is
 * bundled. This avoids showing "connected" while no traffic is flowing.
 */
class VpnTunnelService : VpnService() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = super.onBind(intent)
}
