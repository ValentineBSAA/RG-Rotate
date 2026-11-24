package com.valentinebsaa.rotatemuse;
import android.content.Context;
import android.graphics.*;
import android.view.View;
import android.os.SystemClock;

/** Original procedural demonstrations, not cinematic character videos. */
final class ThemeView extends View {
 final Paint p=new Paint(3); final boolean celestial; boolean animate;
 ThemeView(Context c,boolean celestial,boolean animate){super(c);this.celestial=celestial;this.animate=animate;setContentDescription(celestial?"Celestial Dream procedural night sky":"Neon Nostalgia procedural city");}
 @Override protected void onDraw(Canvas raw){
  super.onDraw(raw); float w=getWidth(),h=getHeight();if(w==0||h==0)return;
  raw.save();raw.scale(w/720,h/720);Canvas c=raw;
  float t=animate?SystemClock.uptimeMillis()/1000f:0;
  p.setShader(new LinearGradient(0,0,720,720,celestial?new int[]{0xff070e25,0xff302052,0xff0a172b}:new int[]{0xff120c2b,0xff532154,0xff09172d},null,Shader.TileMode.CLAMP));c.drawRect(0,0,720,720,p);p.setShader(null);
  p.setColor(celestial?0xffe3c483:0xffff9ec7);p.setAlpha(160);c.drawCircle(490,240,celestial?75:100,p);
  if(celestial){p.setColor(0xff211a3f);c.drawCircle(465,217,68,p);}
  for(int n=0;n<55;n++){float x=(n*137.3f)%720,y=(n*83.7f)%490;p.setColor(celestial?0xffe5d9b5:0xffe69cd9);p.setAlpha((int)(70+65*(1+Math.sin(t*.45+n))));c.drawCircle(x,y,1+n%3*.5f,p);}
  if(!celestial){for(int n=0;n<16;n++){float x=n*49,ht=45+(n*71)%140;p.setColor(0xff11132e);p.setAlpha(255);c.drawRect(x,530-ht,x+40,550,p);p.setColor(0xff98578d);for(int j=0;j<4;j++)c.drawRect(x+9,540-ht+j*28,x+13,548-ht+j*28,p);}
   p.setColor(0xffb44fba);p.setAlpha(75);p.setStrokeWidth(1);for(int n=0;n<10;n++){float y=550+(n*n)*2;c.drawLine(0,y,720,y,p);c.drawLine(360,535,n*100-150,720,p);}}
  // Abstract flowing silhouette: deliberately presented as procedural artwork.
  p.setAlpha(255);p.setColor(celestial?0xff17162f:0xff171027);Path hair=new Path();hair.moveTo(170,645);hair.cubicTo(215,505,137,312,277,217);hair.cubicTo(378,155,438,267,410,370);hair.cubicTo(387,476,463,579,480,720);hair.lineTo(160,720);hair.close();c.drawPath(hair,p);
  p.setColor(celestial?0xffb1a1ca:0xffcf8bae);p.setAlpha(180);RectF face=new RectF(273,259,365,403);c.drawOval(face,p);
  p.setColor(celestial?0xff51435f:0xff672e59);Path fringe=new Path();fringe.moveTo(260,300);fringe.cubicTo(276,200,407,241,363,347);fringe.cubicTo(349,280,310,292,260,300);c.drawPath(fringe,p);
  p.setColor(celestial?0xffd2bd8a:0xffc16bad);p.setAlpha(90);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);for(int n=0;n<5;n++){Path strand=new Path();strand.moveTo(256+n*7,295);strand.cubicTo(175,410,300+(float)Math.sin(t*.5+n)*10,495,204+n*15,670);c.drawPath(strand,p);}p.setStyle(Paint.Style.FILL);p.setAlpha(255);
  raw.restore();if(animate&&isShown())postInvalidateDelayed(42);
 }
}
