package com.valentinebsaa.rotatemuse;

import android.app.Activity;
import android.os.*;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;
import androidx.media3.common.*;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.ui.*;
import java.io.File;
import java.text.SimpleDateFormat;
import java.util.*;

@androidx.media3.common.util.UnstableApi
public class DisplayActivity extends Activity {
 Prefs prefs; FrameLayout root; TextView clock; ExoPlayer player; AnimatedImageDrawable gif;
 final Handler handler=new Handler(Looper.getMainLooper()); long started; boolean running,dragged;
 int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+.5f);}
 @Override public void onCreate(Bundle b){super.onCreate(b);prefs=new Prefs(this);root=new FrameLayout(this);root.setBackgroundColor(Color.BLACK);setContentView(root);
  getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
  clock=new TextView(this);clock.setPadding(dp(14),dp(8),dp(14),dp(8));clock.setTextSize(32);clock.setTextColor(new int[]{0xfff5efff,0xffe5c89d,0xfff3b4d2,0xffb9e4f3}[prefs.i("color",0)]);clock.setAlpha(new float[]{1,.85f,.65f,.45f}[prefs.i("opacity",1)]);clock.setTypeface(Typeface.create(new String[]{"serif","sans-serif-light","monospace"}[prefs.i("font",0)],Typeface.NORMAL));if(prefs.b("shadow",true))clock.setShadowLayer(8,0,2,Color.BLACK);
  FrameLayout.LayoutParams cp=new FrameLayout.LayoutParams(-2,-2,Gravity.TOP|Gravity.LEFT);root.addView(clock,cp);clock.setVisibility(prefs.b("clock",true)?View.VISIBLE:View.GONE);
  clock.setOnTouchListener(new View.OnTouchListener(){float ox,oy;public boolean onTouch(View v,android.view.MotionEvent e){switch(e.getActionMasked()){case android.view.MotionEvent.ACTION_DOWN:ox=e.getRawX()-v.getX();oy=e.getRawY()-v.getY();return true;case android.view.MotionEvent.ACTION_MOVE:v.setX(Math.max(0,Math.min(root.getWidth()-v.getWidth(),e.getRawX()-ox)));v.setY(Math.max(0,Math.min(root.getHeight()-v.getHeight(),e.getRawY()-oy)));return true;case android.view.MotionEvent.ACTION_UP:prefs.set("x",Rules.clamp(v.getX()/Math.max(1,root.getWidth()-v.getWidth())));prefs.set("y",Rules.clamp(v.getY()/Math.max(1,root.getHeight()-v.getHeight())));prefs.set("position",4);dragged=true;v.performClick();return true;}return false;}});
  Button exit=new Button(this);exit.setText("Exit");exit.setAllCaps(false);exit.setTextColor(Color.WHITE);exit.setBackgroundColor(0x66251d32);exit.setContentDescription("Exit display");FrameLayout.LayoutParams ep=new FrameLayout.LayoutParams(dp(72),dp(44),Gravity.TOP|Gravity.RIGHT);ep.setMargins(0,dp(8),dp(8),0);root.addView(exit,ep);exit.setOnClickListener(v->finish());
 }
 @Override protected void onStart(){super.onStart();started=SystemClock.elapsedRealtime();running=true;dragged=false;getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);startMedia();handler.post(tick);}
 void startMedia(){String name=prefs.s("media","");if(name.isEmpty()){demo();return;}File file=new File(new File(getFilesDir(),"media"),name);if(!file.isFile()||!file.getParentFile().equals(new File(getFilesDir(),"media"))){fallback("Imported file is unavailable.");return;}
  if(name.endsWith(".gif")){try{ImageView image=new ImageView(this);image.setScaleType(new ImageView.ScaleType[]{ImageView.ScaleType.FIT_CENTER,ImageView.ScaleType.FIT_XY,ImageView.ScaleType.CENTER_CROP}[prefs.i("fit",0)]);Drawable d=ImageDecoder.decodeDrawable(ImageDecoder.createSource(file),(decoder,info,source)->{int w=info.getSize().getWidth(),h=info.getSize().getHeight();float scale=Math.min(1f,720f/Math.max(w,h));decoder.setTargetSize(Math.max(1,(int)(w*scale)),Math.max(1,(int)(h*scale)));});if(!(d instanceof AnimatedImageDrawable))throw new IllegalArgumentException("The GIF is not animated.");gif=(AnimatedImageDrawable)d;gif.setRepeatCount(AnimatedImageDrawable.REPEAT_INFINITE);image.setImageDrawable(gif);root.addView(image,0,new FrameLayout.LayoutParams(-1,-1));gif.start();prefs.set("playback","Looping GIF");prefs.set("error","None");}catch(Exception e){fallback("GIF could not load. Try a smaller animated GIF.");}return;}
  PlayerView view=new PlayerView(this);view.setUseController(false);view.setResizeMode(new int[]{AspectRatioFrameLayout.RESIZE_MODE_FIT,AspectRatioFrameLayout.RESIZE_MODE_FILL,AspectRatioFrameLayout.RESIZE_MODE_ZOOM}[prefs.i("fit",0)]);root.addView(view,0,new FrameLayout.LayoutParams(-1,-1));
  player=new ExoPlayer.Builder(this).build();view.setPlayer(player);player.setVolume(0);player.setRepeatMode(Player.REPEAT_MODE_ONE);player.addListener(new Player.Listener(){@Override public void onPlayerError(PlaybackException error){fallback("Video cannot play. Try a local H.264 MP4.");}@Override public void onPlaybackStateChanged(int state){prefs.set("playback",state==Player.STATE_READY?"Looping MP4":state==Player.STATE_BUFFERING?"Loading MP4":"Idle");}});player.setMediaItem(MediaItem.fromUri(android.net.Uri.fromFile(file)));player.prepare();player.play();prefs.set("error","None");
 }
 void clearMedia(){if(player!=null){player.release();player=null;}if(gif!=null){gif.stop();gif=null;}while(root.getChildCount()>2)root.removeViewAt(0);}
 void demo(){root.addView(new ThemeView(this,prefs.s("theme","neon").equals("celestial"),true),0,new FrameLayout.LayoutParams(-1,-1));prefs.set("playback","Procedural theme");}
 void fallback(String msg){clearMedia();demo();prefs.set("error",msg);Toast.makeText(this,msg+" Showing the demo theme.",Toast.LENGTH_LONG).show();}
 final Runnable tick=new Runnable(){public void run(){if(!running)return;long now=System.currentTimeMillis();String value=Rules.clock(now,prefs.b("h24",false),prefs.b("seconds",false),TimeZone.getDefault());if(prefs.b("date",true))value+="\n"+new SimpleDateFormat("EEE, MMM d",Locale.getDefault()).format(new Date(now));clock.setText(value);clock.post(()->positionClock());long elapsed=SystemClock.elapsedRealtime()-started;long dim=new long[]{30000,60000,120000,Long.MAX_VALUE}[prefs.i("dim",0)];if(elapsed>=dim){WindowManager.LayoutParams a=getWindow().getAttributes();a.screenBrightness=.08f;getWindow().setAttributes(a);}int minutes=new int[]{2,5,10,0}[prefs.i("sleep",1)];if(Rules.expired(elapsed,minutes)){finish();return;}handler.postDelayed(this,1000);}};
 void positionClock(){if(dragged)return;int pos=prefs.i("position",0);float x=pos==4?prefs.f("x",0):(pos==1||pos==3?1:0);float y=pos==4?prefs.f("y",1):(pos<2?1:0);clock.setX(Rules.clamp(x)*Math.max(0,root.getWidth()-clock.getWidth()));clock.setY(Rules.clamp(y)*Math.max(0,root.getHeight()-clock.getHeight()));}
 @Override protected void onStop(){running=false;handler.removeCallbacksAndMessages(null);clearMedia();getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);WindowManager.LayoutParams a=getWindow().getAttributes();a.screenBrightness=-1;getWindow().setAttributes(a);prefs.set("playback","Stopped (not visible)");super.onStop();}
}
