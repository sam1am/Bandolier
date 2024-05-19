package org.kivy.android;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class PTTReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // Pass the received intent to the Python layer
        PythonActivity.mActivity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                org.kivy.android.PythonActivity.mActivity.onNewIntent(intent);
            }
        });
    }
}