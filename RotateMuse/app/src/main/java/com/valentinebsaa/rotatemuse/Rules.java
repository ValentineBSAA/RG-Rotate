package com.valentinebsaa.rotatemuse;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

public final class Rules {
 private Rules() {}
 public static float clamp(float value) { return Float.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0.5f; }
 public static boolean mediaType(String type) { return "video/mp4".equals(type) || "image/gif".equals(type); }
 public static String clock(long millis, boolean h24, boolean seconds, TimeZone zone) {
  SimpleDateFormat fmt = new SimpleDateFormat((h24 ? "HH:mm" : "h:mm") + (seconds ? ":ss" : "") + (h24 ? "" : " a"), Locale.US);
  fmt.setTimeZone(zone); return fmt.format(new Date(millis));
 }
 public static boolean expired(long elapsed, int minutes) { return minutes > 0 && elapsed >= minutes * 60000L; }
 public static final long MAX_IMPORT = 512L * 1024 * 1024;
}
