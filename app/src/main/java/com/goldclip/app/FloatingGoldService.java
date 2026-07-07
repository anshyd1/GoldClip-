package com.goldclip.app;

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
