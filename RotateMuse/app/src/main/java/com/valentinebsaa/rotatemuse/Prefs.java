package com.valentinebsaa.rotatemuse;
import android.content.Context;
import android.content.SharedPreferences;
final class Prefs {
 final SharedPreferences p;
 Prefs(Context c) { p=c.getSharedPreferences("muse",0); }
 String s(String k,String d){return p.getString(k,d);}
 int i(String k,int d){return p.getInt(k,d);}
 boolean b(String k,boolean d){return p.getBoolean(k,d);}
 float f(String k,float d){return p.getFloat(k,d);}
 void set(String k,String v){p.edit().putString(k,v).apply();}
 void set(String k,int v){p.edit().putInt(k,v).apply();}
 void set(String k,boolean v){p.edit().putBoolean(k,v).apply();}
 void set(String k,float v){p.edit().putFloat(k,v).apply();}
}
