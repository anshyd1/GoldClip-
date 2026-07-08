package com.goldclip.app;

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
