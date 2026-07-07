#!/usr/bin/env python3
"""
✦ GoldClip Bootstrap Script ✦
==============================
Ek hi Python file jo poora Android project bana deti hai.
Sab folders + files khud generate karti hai.

Usage:
    python build_goldclip.py

Ya GitHub Actions workflow se auto-run.
"""
import os
from pathlib import Path

ROOT = Path(".")

FILES = {
    # ═══════════ ROOT ═══════════
    "settings.gradle": """pluginManagement {
    repositories { gradlePluginPortal(); google(); mavenCentral() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "GoldClip"
include ':app'
""",

    "build.gradle": """plugins {
    id 'com.android.application' version '8.2.0' apply false
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
local.properties
""",

    # ═══════════ APP ═══════════
    "app/build.gradle": """plugins { id 'com.android.application' }

android {
    namespace 'com.goldclip.app'
    compileSdk 34
    defaultConfig {
        applicationId "com.goldclip.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release { minifyEnabled false }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
}
""",

    # ═══════════ MANIFEST ═══════════
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:icon="@android:drawable/star_big_on"
        android:label="@string/app_name"
        android:theme="@style/Theme.GoldClip">

        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".FloatingGoldService"
            android:exported="false"
            android:foregroundServiceType="specialUse">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Floating clipboard overlay" />
        </service>

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

    # ═══════════ JAVA FILES ═══════════
    "app/src/main/java/com/goldclip/app/MainActivity.java": """package com.goldclip.app;

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
            Toast.makeText(this, "\\u2726 Started", Toast.LENGTH_SHORT).show();
            moveTaskToBack(true);
        });
    }
}
""",

    "app/src/main/java/com/goldclip/app/ClipboardAccessibilityService.java": """package com.goldclip.app;

import android.accessibilityservice.AccessibilityService;
import android.os.Bundle;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

public class ClipboardAccessibilityService extends AccessibilityService {
    public static ClipboardAccessibilityService instance;

    @Override public void onServiceConnected() { instance = this; }
    @Override public void onAccessibilityEvent(AccessibilityEvent e) {}
    @Override public void onInterrupt() {}
    @Override public boolean onUnbind(android.content.Intent i) {
        instance = null; return super.onUnbind(i);
    }

    private AccessibilityNodeInfo ed() {
        AccessibilityNodeInfo n = findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        return (n != null && n.isEditable()) ? n : null;
    }

    public boolean doSelectAll() {
        AccessibilityNodeInfo n = ed();
        if (n == null) return false;
        CharSequence t = n.getText();
        Bundle a = new Bundle();
        a.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_START_INT, 0);
        a.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_END_INT, t == null ? 0 : t.length());
        return n.performAction(AccessibilityNodeInfo.ACTION_SET_SELECTION, a);
    }

    public boolean doCopy()  { AccessibilityNodeInfo n = ed(); return n != null && n.performAction(AccessibilityNodeInfo.ACTION_COPY); }
    public boolean doPaste() { AccessibilityNodeInfo n = ed(); return n != null && n.performAction(AccessibilityNodeInfo.ACTION_PASTE); }
    public boolean doCut()   { AccessibilityNodeInfo n = ed(); return n != null && n.performAction(AccessibilityNodeInfo.ACTION_CUT); }
}
""",

    "app/src/main/java/com/goldclip/app/FloatingGoldService.java": """package com.goldclip.app;

import android.app.*;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.*;
import android.view.*;
import android.widget.Toast;
import androidx.core.app.NotificationCompat;

public class FloatingGoldService extends Service {
    private WindowManager wm;
    private View ballView, panelView;
    private WindowManager.LayoutParams ballP, panelP;
    private final Handler h = new Handler(Looper.getMainLooper());
    private final Runnable fade = () -> {
        if (ballView != null) ballView.setAlpha(0.15f);
        if (panelView != null) panelView.setAlpha(0.15f);
    };

    @Override public IBinder onBind(Intent i) { return null; }

    @Override
    public void onCreate() {
        super.onCreate();
        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        String ch = "goldclip";
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel c = new NotificationChannel(ch, "GoldClip", NotificationManager.IMPORTANCE_MIN);
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(c);
        }
        startForeground(1, new NotificationCompat.Builder(this, ch)
                .setContentTitle("GoldClip active")
                .setContentText("Floating clipboard running")
                .setSmallIcon(android.R.drawable.star_on)
                .setOngoing(true).build());
        addBall();
    }

    private int type() {
        return Build.VERSION.SDK_INT >= 26
                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                : WindowManager.LayoutParams.TYPE_PHONE;
    }

    private void addBall() {
        ballView = LayoutInflater.from(this).inflate(R.layout.floating_ball, null);
        ballP = new WindowManager.LayoutParams(-2, -2, type(),
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT);
        ballP.gravity = Gravity.TOP | Gravity.START;
        DisplayMetrics dm = getResources().getDisplayMetrics();
        ballP.x = dm.widthPixels - dp(60);
        ballP.y = dm.heightPixels / 3;
        ballView.setOnTouchListener(new Drag(() -> ballP,
                () -> wm.updateViewLayout(ballView, ballP), this::openPanel));
        wm.addView(ballView, ballP);
        arm();
    }

    private void openPanel() {
        if (panelView != null) return;
        panelView = LayoutInflater.from(this).inflate(R.layout.floating_panel, null);
        panelP = new WindowManager.LayoutParams(-2, -2, type(),
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT);
        panelP.gravity = Gravity.TOP | Gravity.START;
        panelP.x = Math.max(dp(10), ballP.x - dp(260));
        panelP.y = Math.max(dp(10), ballP.y - dp(40));

        View dh = panelView.findViewById(R.id.dragHandle);
        dh.setOnTouchListener(new Drag(() -> panelP,
                () -> wm.updateViewLayout(panelView, panelP), null));

        panelView.findViewById(R.id.btnAll).setOnClickListener(v -> act("all"));
        panelView.findViewById(R.id.btnCopy).setOnClickListener(v -> act("copy"));
        panelView.findViewById(R.id.btnPaste).setOnClickListener(v -> act("paste"));
        panelView.findViewById(R.id.btnCut).setOnClickListener(v -> act("cut"));
        panelView.findViewById(R.id.btnHide).setOnClickListener(v -> close());
        panelView.setOnTouchListener((v, e) -> { arm(); return false; });

        wm.addView(panelView, panelP);
        ballView.setVisibility(View.GONE);
        arm();
    }

    private void close() {
        if (panelView != null) { wm.removeView(panelView); panelView = null; }
        ballView.setVisibility(View.VISIBLE);
        arm();
    }

    private void act(String a) {
        ClipboardAccessibilityService s = ClipboardAccessibilityService.instance;
        if (s == null) {
            Toast.makeText(this, "Accessibility ON karo", Toast.LENGTH_SHORT).show();
            return;
        }
        boolean ok = false;
        switch (a) {
            case "all":   ok = s.doSelectAll(); break;
            case "copy":  ok = s.doCopy();      break;
            case "paste": ok = s.doPaste();     break;
            case "cut":   ok = s.doCut();       break;
        }
        Toast.makeText(this, ok ? "OK " + a : "Kuch focused nahi", Toast.LENGTH_SHORT).show();
        arm();
    }

    private void arm() {
        h.removeCallbacks(fade);
        if (ballView != null) ballView.setAlpha(1f);
        if (panelView != null) panelView.setAlpha(1f);
        h.postDelayed(fade, 3000);
    }

    private int dp(int v) { return (int) (v * getResources().getDisplayMetrics().density); }

    @Override
    public void onDestroy() {
        super.onDestroy();
        h.removeCallbacks(fade);
        if (panelView != null) wm.removeView(panelView);
        if (ballView != null) wm.removeView(ballView);
    }

    interface PS { WindowManager.LayoutParams get(); }
    interface UP { void run(); }
    interface CA { void run(); }

    class Drag implements View.OnTouchListener {
        PS ps; UP up; CA ca;
        int sx, sy;
        float tx, ty;
        boolean m;
        Drag(PS a, UP b, CA c) { ps = a; up = b; ca = c; }
        public boolean onTouch(View v, MotionEvent e) {
            arm();
            WindowManager.LayoutParams p = ps.get();
            switch (e.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    sx = p.x; sy = p.y; tx = e.getRawX(); ty = e.getRawY(); m = false;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    int dx = (int) (e.getRawX() - tx), dy = (int) (e.getRawY() - ty);
                    if (Math.abs(dx) + Math.abs(dy) > 10) m = true;
                    p.x = sx + dx; p.y = sy + dy;
                    up.run();
                    return true;
                case MotionEvent.ACTION_UP:
                    if (!m && ca != null) ca.run();
                    return true;
            }
            return false;
        }
    }
}
""",

    # ═══════════ LAYOUTS ═══════════
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
        android:text="\\u2726 GoldClip"
        android:textSize="34sp"
        android:textStyle="bold"
        android:textColor="@color/gold_dark"/>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="32dp"
        android:text="Floating clipboard tool"
        android:textColor="@color/gold_dark"
        android:alpha="0.7"/>

    <Button android:id="@+id/btnAccessibility"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="Step 1: Enable Accessibility"
        android:backgroundTint="@color/gold"
        android:textColor="@color/cream"/>

    <Button android:id="@+id/btnOverlay"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="12dp"
        android:text="Step 2: Allow Overlay"
        android:backgroundTint="@color/gold"
        android:textColor="@color/cream"/>

    <Button android:id="@+id/btnStart"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="12dp"
        android:text="Step 3: Start GoldClip"
        android:backgroundTint="@color/gold_dark"
        android:textColor="@color/cream"/>
</LinearLayout>
""",

    "app/src/main/res/layout/floating_ball.xml": """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:padding="4dp">

    <FrameLayout
        android:layout_width="52dp"
        android:layout_height="52dp"
        android:background="@drawable/bg_pearl_ring">

        <View
            android:layout_width="30dp"
            android:layout_height="30dp"
            android:layout_gravity="center"
            android:background="@drawable/bg_gold_ball"/>

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center_vertical|start"
            android:layout_marginStart="6dp"
            android:text="\\u2039"
            android:textStyle="bold"
            android:textSize="18sp"
            android:textColor="@color/gold_dark"/>
    </FrameLayout>
</FrameLayout>
""",

    "app/src/main/res/layout/floating_panel.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="240dp"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:background="@drawable/bg_panel"
    android:padding="12dp">

    <View android:id="@+id/dragHandle"
        android:layout_width="60dp"
        android:layout_height="4dp"
        android:layout_gravity="center_horizontal"
        android:layout_marginBottom="10dp"
        android:background="@color/gold"/>

    <LinearLayout android:id="@+id/btnAll"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:padding="14dp"
        android:layout_marginBottom="8dp"
        android:background="@drawable/bg_card" android:gravity="center_vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="A" android:textSize="20sp" android:textStyle="bold"
            android:layout_marginEnd="14dp" android:textColor="@color/gold_dark"/>
        <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="vertical">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Ctrl + A" android:textStyle="bold" android:textSize="15sp" android:textColor="#3a2a00"/>
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Select All" android:textSize="12sp" android:textColor="@color/gold_dark"/>
        </LinearLayout>
    </LinearLayout>

    <LinearLayout android:id="@+id/btnCopy"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:padding="14dp"
        android:layout_marginBottom="8dp"
        android:background="@drawable/bg_card" android:gravity="center_vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="C" android:textSize="20sp" android:textStyle="bold"
            android:layout_marginEnd="14dp" android:textColor="@color/gold_dark"/>
        <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="vertical">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Ctrl + C" android:textStyle="bold" android:textSize="15sp" android:textColor="#3a2a00"/>
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Copy" android:textSize="12sp" android:textColor="@color/gold_dark"/>
        </LinearLayout>
    </LinearLayout>

    <LinearLayout android:id="@+id/btnPaste"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:padding="14dp"
        android:layout_marginBottom="8dp"
        android:background="@drawable/bg_card" android:gravity="center_vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="V" android:textSize="20sp" android:textStyle="bold"
            android:layout_marginEnd="14dp" android:textColor="@color/gold_dark"/>
        <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="vertical">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Ctrl + V" android:textStyle="bold" android:textSize="15sp" android:textColor="#3a2a00"/>
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Paste" android:textSize="12sp" android:textColor="@color/gold_dark"/>
        </LinearLayout>
    </LinearLayout>

    <LinearLayout android:id="@+id/btnCut"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:padding="14dp"
        android:layout_marginBottom="10dp"
        android:background="@drawable/bg_card" android:gravity="center_vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="X" android:textSize="20sp" android:textStyle="bold"
            android:layout_marginEnd="14dp" android:textColor="@color/gold_dark"/>
        <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="vertical">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Ctrl + X" android:textStyle="bold" android:textSize="15sp" android:textColor="#3a2a00"/>
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Cut" android:textSize="12sp" android:textColor="@color/gold_dark"/>
        </LinearLayout>
    </LinearLayout>

    <Button android:id="@+id/btnHide"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center_horizontal"
        android:text="Hide"
        android:textColor="@color/gold_dark"
        android:background="@drawable/bg_card"/>
</LinearLayout>
""",

    # ═══════════ DRAWABLES ═══════════
    "app/src/main/res/drawable/bg_gold_ball.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient
        android:type="radial"
        android:gradientRadius="20dp"
        android:centerX="0.35"
        android:centerY="0.35"
        android:startColor="#FFF7C0"
        android:centerColor="#FFD700"
        android:endColor="#B8860B"/>
</shape>
""",

    "app/src/main/res/drawable/bg_pearl_ring.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFFDF6"/>
    <stroke android:width="1.5dp" android:color="#D4AF37"/>
</shape>
""",

    "app/src/main/res/drawable/bg_panel.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFDF6"/>
    <stroke android:width="1.5dp" android:color="#D4AF37"/>
    <corners android:radius="18dp"/>
</shape>
""",

    "app/src/main/res/drawable/bg_card.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFBEA"/>
    <stroke android:width="1dp" android:color="#D4AF37"/>
    <corners android:radius="12dp"/>
</shape>
""",

    # ═══════════ VALUES ═══════════
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
    <style name="Theme.GoldClip" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">@color/gold</item>
        <item name="colorPrimaryDark">@color/gold_dark</item>
        <item name="colorAccent">@color/gold</item>
    </style>
</resources>
""",

    # ═══════════ XML CONFIG ═══════════
    "app/src/main/res/xml/accessibility_service_config.xml": """<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeViewFocused|typeViewTextSelectionChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows"
    android:canRetrieveWindowContent="true"
    android:description="@string/app_name"
    android:notificationTimeout="100"/>
""",

    # ═══════════ README ═══════════
    "README.md": """# GoldClip

Android floating Ctrl+A / Ctrl+C / Ctrl+V / Ctrl+X clipboard tool.

## Features
- Floating gold ball on screen
- Tap to expand panel with 4 buttons
- Auto-fade after 3 seconds
- Draggable anywhere
- Works in any app via Accessibility Service

## Build
1. Open in Android Studio
2. Sync Gradle
3. Run on device (Android 7.0+)

## Setup
1. Enable Accessibility Service (GoldClip)
2. Allow Overlay permission
3. Tap "Start GoldClip"

## License
MIT
""",
}


def main():
    print("=" * 50)
    print("  GoldClip Project Builder")
    print("=" * 50)
    created = 0
    for rel_path, content in FILES.items():
        p = ROOT / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"  [+] {rel_path}")
        created += 1
    print("=" * 50)
    print(f"  Done! {created} files created.")
    print(f"  Folders: {len(set(str(Path(p).parent) for p in FILES))} unique dirs")
    print("=" * 50)


if __name__ == "__main__":
    main()
