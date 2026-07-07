package com.goldclip.app;

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
