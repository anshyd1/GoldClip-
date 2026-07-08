package com.goldclip.app;

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
