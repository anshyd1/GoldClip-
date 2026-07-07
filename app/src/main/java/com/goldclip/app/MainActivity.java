package com.goldclip.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);

        Button step1 = findViewById(R.id.btnAccessibility);
        Button step2 = findViewById(R.id.btnOverlay);
        Button step3 = findViewById(R.id.btnStart);

        step1.setOnClickListener(v ->
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));

        step2.setOnClickListener(v -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                if (!Settings.canDrawOverlays(this)) {
                    startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:" + getPackageName())));
                } else {
                    Toast.makeText(this, "Overlay OK", Toast.LENGTH_SHORT).show();
                }
            }
        });

        step3.setOnClickListener(v -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                    && !Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Pehle Overlay do", Toast.LENGTH_SHORT).show();
                return;
            }
            Intent i = new Intent(this, FloatingGoldService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                startForegroundService(i);
            else startService(i);
            Toast.makeText(this, "\u2726 Started", Toast.LENGTH_SHORT).show();
            moveTaskToBack(true);
        });
    }
}
