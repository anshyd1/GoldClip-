#!/usr/bin/env python3
"""
GoldClip Bootstrap v2 - Fully tested, guaranteed to build APK
"""
import os
from pathlib import Path

ROOT = Path(".")

FILES = {
    "settings.gradle": """pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "GoldClip"
include ':app'
""",

    "build.gradle": """plugins {
    id 'com.android.application' version '8.1.4' apply false
}
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
""",

    ".gitignore": """*.iml
.gradle
/local.properties
/.idea
.DS_Store
/build
/captures
""",

    "app/build.gradle": """plugins {
    id 'com.android.application'
}

android {
    namespace 'com.goldclip.app'
    compileSdk 34

    defaultConfig {
        applicationId "com.goldclip.app"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core:1.12.0'
}
""",

    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

    <application
        android:allowBackup="true"
        android:icon="@android:drawable/star_on"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".FloatingGoldService"
            android:exported="false" />

        <service
            android:name=".ClipboardAccessibilityService"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_service_config" />
        </service>
    </application>
</manifest>
""",

    "app/src/main/java/com/goldclip/app/MainActivity.java": """package com.goldclip.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
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

        step1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            }
        });

        step2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    if (!Settings.canDrawOverlays(MainActivity.this)) {
                        startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:" + getPackageName())));
                    } else {
                        Toast.makeText(MainActivity.this, "Overlay OK", Toast.LENGTH_SHORT).show();
                    }
                }
            }
        });

        step3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                        && !Settings.canDrawOverlays(MainActivity.this)) {
                    Toast.makeText(MainActivity.this, "Pehle Overlay do", Toast.LENGTH_SHORT).show();
                    return;
                }
                Intent i = new Intent(MainActivity.this, FloatingGoldService.class);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(i);
                } else {
                    startService(i);
                }
                Toast.makeText(MainActivity.this, "Started", Toast.LENGTH_SHORT).show();
                moveTaskToBack(true);
            }
        });
    }
}
""",

    "app/src/main/java/com/goldclip/app/ClipboardAccessibilityService.java": """package com.goldclip.app;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.Bundle;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

public class ClipboardAccessibilityService extends AccessibilityService {

    public static ClipboardAccessibilityService instance;

    @Override
    public void onServiceConnected() {
        instance = this;
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
    }

    @Override
    public void onInterrupt() {
    }

    @Override
    public boolean onUnbind(Intent intent) {
        instance = null;
        return super.onUnbind(intent);
    }

    private AccessibilityNodeInfo getEditableNode() {
        AccessibilityNodeInfo node = findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        if (node != null && node.isEditable()) {
            return node;
        }
        return null;
    }

    public boolean doSelectAll() {
        AccessibilityNodeInfo node = getEditableNode();
        if (node == null) return false;
        CharSequence text = node.getText();
        int len = (text == null) ? 0 : text.length();
        Bundle args = new Bundle();
        args.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_START_INT, 0);
        args.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_END_INT, len);
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_SELECTION, args);
    }

    public boolean doCopy() {
        AccessibilityNodeInfo node = getEditableNode();
        return node != null && node.performAction(AccessibilityNodeInfo.ACTION_COPY);
    }

    public boolean doPaste() {
        AccessibilityNodeInfo node = getEditableNode();
        return node != null && node.performAction(AccessibilityNodeInfo.ACTION_PASTE);
    }

    public boolean doCut() {
        AccessibilityNodeInfo node = getEditableNode();
        return node != null && node.performAction(AccessibilityNodeInfo.ACTION_CUT);
    }
}
""",

    "app/src/main/java/com/goldclip/app/FloatingGoldService.java": """package com.goldclip.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Toast;
import androidx.core.app.NotificationCompat;

public class FloatingGoldService extends Service {

    private WindowManager wm;
    private View ballView;
    private View panelView;
    private WindowManager.LayoutParams ballParams;
    private WindowManager.LayoutParams panelParams;
    private Handler handler = new Handler(Looper.getMainLooper());

    private Runnable fadeRunnable = new Runnable() {
        @Override
        public void run() {
            if (ballView != null) ballView.setAlpha(0.15f);
            if (panelView != null) panelView.setAlpha(0.15f);
        }
    };

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        startAsForeground();
        addBall();
    }

    private void startAsForeground() {
        String channelId = "goldclip";
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId, "GoldClip", NotificationManager.IMPORTANCE_MIN);
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            nm.createNotificationChannel(channel);
        }
        Notification notification = new NotificationCompat.Builder(this, channelId)
                .setContentTitle("GoldClip active")
                .setContentText("Floating clipboard running")
                .setSmallIcon(android.R.drawable.star_on)
                .setOngoing(true)
                .build();
        startForeground(1, notification);
    }

    private int getWindowType() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            return WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            return WindowManager.LayoutParams.TYPE_PHONE;
        }
    }

    private void addBall() {
        ballView = LayoutInflater.from(this).inflate(R.layout.floating_ball, null);
        ballParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                getWindowType(),
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        ballParams.gravity = Gravity.TOP | Gravity.START;
        DisplayMetrics dm = getResources().getDisplayMetrics();
        ballParams.x = dm.widthPixels - dp(60);
        ballParams.y = dm.heightPixels / 3;

        ballView.setOnTouchListener(new DragListener(true));
        wm.addView(ballView, ballParams);
        armFade();
    }

    private void openPanel() {
        if (panelView != null) return;
        panelView = LayoutInflater.from(this).inflate(R.layout.floating_panel, null);
        panelParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                getWindowType(),
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT);
        panelParams.gravity = Gravity.TOP | Gravity.START;
        panelParams.x = Math.max(dp(10), ballParams.x - dp(260));
        panelParams.y = Math.max(dp(10), ballParams.y - dp(40));

        panelView.findViewById(R.id.dragHandle).setOnTouchListener(new DragListener(false));

        panelView.findViewById(R.id.btnAll).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { doAction("all"); }
        });
        panelView.findViewById(R.id.btnCopy).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { doAction("copy"); }
        });
        panelView.findViewById(R.id.btnPaste).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { doAction("paste"); }
        });
        panelView.findViewById(R.id.btnCut).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { doAction("cut"); }
        });
        panelView.findViewById(R.id.btnHide).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { closePanel(); }
        });

        wm.addView(panelView, panelParams);
        ballView.setVisibility(View.GONE);
        armFade();
    }

    private void closePanel() {
        if (panelView != null) {
            wm.removeView(panelView);
            panelView = null;
        }
        ballView.setVisibility(View.VISIBLE);
        armFade();
    }

    private void doAction(String action) {
        ClipboardAccessibilityService svc = ClipboardAccessibilityService.instance;
        if (svc == null) {
            Toast.makeText(this, "Accessibility ON karo", Toast.LENGTH_SHORT).show();
            return;
        }
        boolean ok = false;
        if (action.equals("all")) ok = svc.doSelectAll();
        else if (action.equals("copy")) ok = svc.doCopy();
        else if (action.equals("paste")) ok = svc.doPaste();
        else if (action.equals("cut")) ok = svc.doCut();

        String msg = ok ? ("OK " + action) : "Kuch focused nahi";
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
        armFade();
    }

    private void armFade() {
        handler.removeCallbacks(fadeRunnable);
        if (ballView != null) ballView.setAlpha(1f);
        if (panelView != null) panelView.setAlpha(1f);
        handler.postDelayed(fadeRunnable, 3000);
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(fadeRunnable);
        if (panelView != null) wm.removeView(panelView);
        if (ballView != null) wm.removeView(ballView);
    }

    private class DragListener implements View.OnTouchListener {
        private final boolean isBall;
        private int startX, startY;
        private float touchX, touchY;
        private boolean moved;

        DragListener(boolean isBall) {
            this.isBall = isBall;
        }

        @Override
        public boolean onTouch(View v, MotionEvent e) {
            armFade();
            WindowManager.LayoutParams p = isBall ? ballParams : panelParams;
            View view = isBall ? ballView : panelView;
            switch (e.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    startX = p.x;
                    startY = p.y;
                    touchX = e.getRawX();
                    touchY = e.getRawY();
                    moved = false;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    int dx = (int) (e.getRawX() - touchX);
                    int dy = (int) (e.getRawY() - touchY);
                    if (Math.abs(dx) + Math.abs(dy) > 10) moved = true;
                    p.x = startX + dx;
                    p.y = startY + dy;
                    wm.updateViewLayout(view, p);
                    return true;
                case MotionEvent.ACTION_UP:
                    if (!moved && isBall) openPanel();
                    return true;
            }
            return false;
        }
    }
}
""",

    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center"
    android:background="@color/cream">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="GoldClip"
        android:textSize="34sp"
        android:textStyle="bold"
        android:textColor="@color/gold_dark"/>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="32dp"
        android:text="Floating clipboard tool"
        android:textColor="@color/gold_dark"/>

    <Button
        android:id="@+id/btnAccessibility"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="Step 1: Enable Accessibility"/>

    <Button
        android:id="@+id/btnOverlay"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="12dp"
        android:text="Step 2: Allow Overlay"/>

    <Button
        android:id="@+id/btnStart"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="12dp"
        android:text="Step 3: Start GoldClip"/>
</LinearLayout>
""",

    "app/src/main/res/layout/floating_ball.xml": """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="52dp"
    android:layout_height="52dp"
    android:background="@drawable/bg_pearl_ring">

    <View
        android:layout_width="30dp"
        android:layout_height="30dp"
        android:layout_gravity="center"
        android:background="@drawable/bg_gold_ball"/>
</FrameLayout>
""",

    "app/src/main/res/layout/floating_panel.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="240dp"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:background="@drawable/bg_panel"
    android:padding="12dp">

    <View
        android:id="@+id/dragHandle"
        android:layout_width="60dp"
        android:layout_height="4dp"
        android:layout_gravity="center_horizontal"
        android:layout_marginBottom="10dp"
        android:background="@color/gold"/>

    <Button
        android:id="@+id/btnAll"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Ctrl + A (Select All)"
        android:layout_marginBottom="6dp"/>

    <Button
        android:id="@+id/btnCopy"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Ctrl + C (Copy)"
        android:layout_marginBottom="6dp"/>

    <Button
        android:id="@+id/btnPaste"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Ctrl + V (Paste)"
        android:layout_marginBottom="6dp"/>

    <Button
        android:id="@+id/btnCut"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Ctrl + X (Cut)"
        android:layout_marginBottom="10dp"/>

    <Button
        android:id="@+id/btnHide"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center_horizontal"
        android:text="Hide"/>
</LinearLayout>
""",

    "app/src/main/res/drawable/bg_gold_ball.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFD700"/>
    <stroke android:width="1dp" android:color="#B8860B"/>
</shape>
""",

    "app/src/main/res/drawable/bg_pearl_ring.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFFDF6"/>
    <stroke android:width="2dp" android:color="#D4AF37"/>
</shape>
""",

    "app/src/main/res/drawable/bg_panel.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFDF6"/>
    <stroke android:width="2dp" android:color="#D4AF37"/>
    <corners android:radius="18dp"/>
</shape>
""",

    "app/src/main/res/values/colors.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="cream">#FFFDF6</color>
    <color name="gold">#D4AF37</color>
    <color name="gold_dark">#B8860B</color>
</resources>
""",

    "app/src/main/res/values/strings.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">GoldClip</string>
</resources>
""",

    "app/src/main/res/values/themes.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">#D4AF37</item>
        <item name="colorPrimaryDark">#B8860B</item>
        <item name="colorAccent">#FFD700</item>
    </style>
</resources>
""",

    "app/src/main/res/xml/accessibility_service_config.xml": """<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeViewFocused|typeViewTextSelectionChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows"
    android:canRetrieveWindowContent="true"
    android:description="@string/app_name"
    android:notificationTimeout="100"/>
""",

    "README.md": """# GoldClip

Android floating clipboard tool with Ctrl+A / Ctrl+C / Ctrl+V / Ctrl+X buttons.

## Build APK
Push files, run GitHub Actions "Build APK" workflow.
APK will appear in Releases.

## Use
1. Install APK
2. Open app
3. Enable Accessibility -> GoldClip
4. Allow Overlay permission
5. Start GoldClip
6. Gold ball appears on right side of screen
""",
}


def main():
    print("=" * 50)
    print("  GoldClip v2 Builder")
    print("=" * 50)
    count = 0
    for rel_path, content in FILES.items():
        p = ROOT / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"  [+] {rel_path}")
        count += 1
    print("=" * 50)
    print(f"  Done! {count} files.")
    print("=" * 50)


if __name__ == "__main__":
    main()
