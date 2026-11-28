package com.rotateradio.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
import android.database.Cursor;
import android.graphics.Color;
import android.media.*;
import android.net.Uri;
import android.os.Bundle;
import android.provider.DocumentsContract;
import android.provider.DocumentsContract.Document;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.nio.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicBoolean;

public class MainActivity extends Activity {
 final int BG=0xff11151e, PANEL=0xff212a3b, TEXT=0xffedf2ff, BLUE=0xff9dbaff;
 final String[] labels={"Liberty City Stories · USA/Korea","Liberty City Stories · Europe","Liberty City Stories · Germany","Liberty City Stories · Japan","Vice City Stories · USA","Vice City Stories · Europe","Vice City Stories · Germany","Vice City Stories · Japan","Both GTA games · USA"};
 final String[][] ids={{"ULUS10041"},{"ULES00151"},{"ULES00182"},{"ULJM05255"},{"ULUS10160"},{"ULES00502"},{"ULES00503"},{"ULJM05297"},{"ULUS10041","ULUS10160"}};
 Uri source, destination;
 TextView sourceText,destText,log,progressText;
 ProgressBar progress;
 Button start, cancel, sourceButton,destButton;
 Spinner game;
 final ExecutorService executor=Executors.newSingleThreadExecutor();
 final AtomicBoolean stopped=new AtomicBoolean();
 volatile Process encoder;
 boolean busy;
 int dp(float n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
 TextView txt(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
 Button btn(String s,Runnable f){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setOnClickListener(v->f.run());return b;}
 void add(LinearLayout l,View v){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(4),0,dp(4));l.addView(v,p);}
 @Override public void onCreate(Bundle state){super.onCreate(state);
  source=load("source");destination=load("destination");
  ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(BG);
  LinearLayout l=new LinearLayout(this);l.setOrientation(1);l.setPadding(dp(16),dp(12),dp(16),dp(12));scroll.addView(l);setContentView(scroll);
  add(l,txt("ROTATE RADIO",25,BLUE));add(l,txt("0.1.0  /  Hardware alpha",12,0xffaab6ca));
  sourceButton=btn("1  ·  Choose music folder",()->pick(11));add(l,sourceButton);sourceText=txt("",13,TEXT);add(l,sourceText);
  destButton=btn("2  ·  Choose PPSSPP PSP folder",()->pick(12));add(l,destButton);destText=txt("",13,TEXT);add(l,destText);
  game=new Spinner(this);ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_item,labels);a.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);game.setAdapter(a);game.setSelection(getPreferences(0).getInt("game",0));add(l,game);
  add(l,txt("ATRAC3 LP4 • experimental • additive install",12,BLUE));
  start=btn("Convert & install",this::confirm);add(l,start);
  cancel=btn("Cancel safely",()->{stopped.set(true);Process p=encoder;if(p!=null)p.destroy();});cancel.setEnabled(false);add(l,cancel);
  progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);add(l,progress);
  progressText=txt("Ready",13,TEXT);add(l,progressText);
  log=txt("Close GTA before installing. Existing music is preserved. Use PairDrop to transfer music, then pick its folder.",12,0xffb9c7da);log.setTextIsSelectable(true);add(l,log);
  refresh();
 }
 Uri load(String key){String x=getPreferences(0).getString(key,null);return x==null?null:Uri.parse(x);}
 void refresh(){sourceText.setText(source==null?"No music folder selected":shortUri(source));destText.setText(destination==null?"No PPSSPP folder selected":shortUri(destination));start.setEnabled(!busy&&source!=null&&destination!=null);}
 String shortUri(Uri u){try{return DocumentsContract.getTreeDocumentId(u);}catch(Exception e){return u.toString();}}
 void pick(int req){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);startActivityForResult(i,req);}
 @Override protected void onActivityResult(int r,int result,Intent i){super.onActivityResult(r,result,i);if(result!=RESULT_OK||i==null||i.getData()==null)return;Uri u=i.getData();int flags=i.getFlags()&(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);try{getContentResolver().takePersistableUriPermission(u,flags);if(r==11)source=u;else if(r==12){if((flags&Intent.FLAG_GRANT_WRITE_URI_PERMISSION)==0)throw new IOException("Folder is read-only");destination=u;}getPreferences(0).edit().putString(r==11?"source":"destination",u.toString()).apply();refresh();}catch(Exception e){new AlertDialog.Builder(this).setMessage("Folder permission failed: "+e.getMessage()).setPositiveButton("OK",null).show();}}
 void confirm(){int target=game.getSelectedItemPosition();new AlertDialog.Builder(this).setTitle("Install station pack?").setMessage("Close GTA first. Tracks will be added to "+labels[target]+". No original files will be replaced. Try a folder with two tracks first.").setNegativeButton("Cancel",null).setPositiveButton("Install",(d,w)->runBatch(target)).show();}
 void line(String s){runOnUiThread(()->{String old=log.getText().toString();if(old.length()>14000)old=old.substring(old.length()-10000);log.setText(old+"\n"+s);});}
 void status(int done,int total,String s){runOnUiThread(()->{progress.setMax(Math.max(1,total));progress.setProgress(done);progressText.setText(s);});}
 void check()throws IOException{if(stopped.get())throw new IOException("Cancelled");}
 class D {
  final Uri tree,uri;final String id,name,mime;
  D(Uri t,String id,String n,String m){tree=t;this.id=id;name=n;mime=m;uri=DocumentsContract.buildDocumentUriUsingTree(t,id);}
  boolean dir(){return Document.MIME_TYPE_DIR.equals(mime);}
  List<D> children()throws IOException{List<D> out=new ArrayList<>();Uri list=DocumentsContract.buildChildDocumentsUriUsingTree(tree,id);String[] cols={Document.COLUMN_DOCUMENT_ID,Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE};try(Cursor c=getContentResolver().query(list,cols,null,null,null)){if(c==null)throw new IOException("Cannot list "+name);while(c.moveToNext())out.add(new D(tree,c.getString(0),c.getString(1),c.getString(2)));}out.sort(Comparator.comparing(x->x.name.toLowerCase(Locale.ROOT)));return out;}
  D child(String n)throws IOException{for(D x:children())if(n.equalsIgnoreCase(x.name))return x;return null;}
  D mkdir(String n)throws IOException{D x=child(n);if(x!=null){if(!x.dir())throw new IOException(n+" is not a folder");return x;}Uri made=DocumentsContract.createDocument(getContentResolver(),uri,Document.MIME_TYPE_DIR,n);if(made==null)throw new IOException("Cannot create "+n);return new D(tree,DocumentsContract.getDocumentId(made),n,Document.MIME_TYPE_DIR);}
 }
 D root(Uri t)throws IOException{String id=DocumentsContract.getTreeDocumentId(t);Uri u=DocumentsContract.buildDocumentUriUsingTree(t,id);try(Cursor c=getContentResolver().query(u,new String[]{Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE},null,null,null)){if(c==null||!c.moveToFirst())throw new IOException("Folder unavailable");return new D(t,id,c.getString(0),c.getString(1));}}
 D saveDir(Uri t)throws IOException{D r=root(t);if("SAVEDATA".equalsIgnoreCase(r.name))return r;D p="PSP".equalsIgnoreCase(r.name)?r:r.child("PSP");if(p==null||!p.dir())throw new IOException("Select the existing PSP or SAVEDATA folder");D s=p.child("SAVEDATA");if(s==null||!s.dir())throw new IOException("Existing SAVEDATA not found. Start PPSSPP first.");return s;}
 boolean supported(String n){return n.toLowerCase(Locale.ROOT).matches(".*\\.(mp3|m4a|aac|wav|flac|ogg|opus|at3|gta)$");}
 void scan(D d,List<D> out,int depth,Set<String> seen)throws IOException{check();if(depth>20||!seen.add(d.id))return;for(D x:d.children()){if(x.dir())scan(x,out,depth+1,seen);else if(supported(x.name)){if(out.size()>=1000)throw new IOException("Folder exceeds 1000 supported files; split it into smaller packs");out.add(x);}}}
 void runBatch(int target){busy=true;stopped.set(false);start.setEnabled(false);cancel.setEnabled(true);sourceButton.setEnabled(false);destButton.setEnabled(false);game.setEnabled(false);getPreferences(0).edit().putInt("game",target).apply();Uri src=source,dst=destination;log.setText("Scanning...");executor.submit(()->{int ok=0,fail=0,skip=0;try{
  D s=saveDir(dst);D input=root(src);
  // Never scan a destination tree, which may contain game saves.
  if(src.equals(dst)||input.id.equals(s.id)||input.id.toLowerCase(Locale.ROOT).endsWith(":psp")||input.name.equalsIgnoreCase("PSP")||input.name.equalsIgnoreCase("SAVEDATA"))throw new IOException("Choose a separate music folder, not PPSSPP data.");
  List<D> tracks=new ArrayList<>();scan(input,tracks,0,new HashSet<>());if(tracks.isEmpty())throw new IOException("No supported music files found");
  List<D> outputs=new ArrayList<>();for(String id:ids[target])outputs.add(s.mkdir(id+"CUSTOMTRACKS"));
  for(int i=0;i<tracks.size();i++){check();D track=tracks.get(i);status(i,tracks.size(),"Track "+(i+1)+"/"+tracks.size()+": "+track.name);
   File raw=File.createTempFile("rr-input-",".tmp",getCacheDir()),wav=null,at3=null;
   try{try(InputStream in=getContentResolver().openInputStream(track.uri);OutputStream out=new FileOutputStream(raw)){if(in==null)throw new IOException("Cannot open input");copy(in,out,512L*1024*1024);}
    String lower=track.name.toLowerCase(Locale.ROOT);File ready;
    if(lower.endsWith(".at3")||lower.endsWith(".gta")){ready=raw;}else{wav=File.createTempFile("rr-pcm-",".wav",getCacheDir());decode(raw,wav);check();at3=File.createTempFile("rr-atrac-",".at3",getCacheDir());encode(wav,at3);ready=at3;}
    validateAtrac(ready);String hash=sha(ready);String base=track.name.replaceFirst("\\.[^.]+$","").replaceAll("[^A-Za-z0-9 _.-]","_");if(base.length()>48)base=base.substring(0,48);String name="RR-"+hash.substring(0,16)+"-"+base+".gta";boolean added=false;
    for(D dest:outputs){check();D exists=null;for(D candidate:dest.children()){if(candidate.name.startsWith("RR-"+hash.substring(0,16)+"-")&&candidate.name.endsWith(".gta")){try(InputStream prior=getContentResolver().openInputStream(candidate.uri)){if(prior!=null&&hash.equals(sha(prior))){exists=candidate;break;}}}}if(exists!=null){line("Already installed: "+track.name+" / "+dest.name);continue;}if(dest.child(name)!=null)throw new IOException("Filename collision; existing file kept");install(ready,dest,name,hash);added=true;}
    if(added){ok++;line("Installed: "+track.name);}else skip++;
   }catch(Exception e){if(stopped.get())throw e;fail++;line("FAILED "+track.name+": "+e.getMessage());}finally{raw.delete();if(wav!=null)wav.delete();if(at3!=null)at3.delete();}
  }status(tracks.size(),tracks.size(),"Finished");line("Installed "+ok+" · Already present "+skip+" · Failed "+fail);
 }catch(Exception e){line("Stopped: "+e.getMessage()+" (completed tracks kept)");}finally{runOnUiThread(()->{busy=false;cancel.setEnabled(false);sourceButton.setEnabled(true);destButton.setEnabled(true);game.setEnabled(true);refresh();});}});}
 void copy(InputStream in,OutputStream out,long limit)throws Exception{byte[] b=new byte[65536];int n;long total=0;while((n=in.read(b))!=-1){check();total+=n;if(total>limit)throw new IOException("File exceeds safety limit");out.write(b,0,n);}}
 String sha(File f)throws Exception{try(InputStream in=new FileInputStream(f)){return sha(in);}}
 String sha(InputStream in)throws Exception{MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1){check();d.update(b,0,n);}StringBuilder s=new StringBuilder();for(byte x:d.digest())s.append(String.format(Locale.ROOT,"%02x",x&255));return s.toString();}
 void install(File f,D dest,String name,String digest)throws Exception{
  Uri tmp=DocumentsContract.createDocument(getContentResolver(),dest.uri,"application/octet-stream","RR-stage-"+UUID.randomUUID()+".part");if(tmp==null)throw new IOException("Cannot create staging file");boolean committed=false;
  try{try(InputStream in=new FileInputStream(f);OutputStream out=getContentResolver().openOutputStream(tmp,"w")){if(out==null)throw new IOException("Cannot write staging file");copy(in,out,512L*1024*1024);}
   try(InputStream in=getContentResolver().openInputStream(tmp)){if(in==null||!digest.equals(sha(in)))throw new IOException("Copy checksum mismatch");}
   check();if(dest.child(name)!=null)throw new IOException("Existing file kept");Uri fin=DocumentsContract.renameDocument(getContentResolver(),tmp,name);if(fin==null)throw new IOException("Provider cannot rename safely");committed=true;
  }finally{if(!committed)try{DocumentsContract.deleteDocument(getContentResolver(),tmp);}catch(Exception ignored){}}
 }
 void encode(File wav,File out)throws Exception{
  File bin=new File(getApplicationInfo().nativeLibraryDir,"libatracdenc.so");if(!bin.canExecute())throw new IOException("Native encoder unavailable");
  Process p=new ProcessBuilder(bin.getAbsolutePath(),"-e","atrac3-lp4","--container","riff","-i",wav.getAbsolutePath(),"-o",out.getAbsolutePath()).redirectErrorStream(true).start();encoder=p;
  try{ByteArrayOutputStream tail=new ByteArrayOutputStream();try(InputStream in=p.getInputStream()){byte[] b=new byte[2048];int n;while((n=in.read(b))!=-1){check();if(tail.size()>6000)tail.reset();tail.write(b,0,n);}}int exit=p.waitFor();check();if(exit!=0)throw new IOException("ATRAC encoder exit "+exit+": "+tail.toString("UTF-8"));}finally{p.destroy();encoder=null;}
 }
 static int le16(RandomAccessFile r)throws IOException{return r.readUnsignedByte()|(r.readUnsignedByte()<<8);}
 static long le32(RandomAccessFile r)throws IOException{return Integer.toUnsignedLong(Integer.reverseBytes(r.readInt()));}
 void validateAtrac(File f)throws IOException{try(RandomAccessFile r=new RandomAccessFile(f,"r")){if(r.length()<44||r.readInt()!=0x52494646)throw new IOException("Not RIFF ATRAC");long declared=le32(r)+8;if(declared>r.length()||r.readInt()!=0x57415645)throw new IOException("Incomplete WAVE");boolean fmt=false;long data=0,rate=0,fact=0,sampleRate=0;while(r.getFilePointer()+8<=declared){int tag=r.readInt();long size=le32(r),p=r.getFilePointer();if(size>declared-p)throw new IOException("Truncated ATRAC chunk");if(tag==0x666d7420&&size>=16){int codec=le16(r);int channels=le16(r);sampleRate=le32(r);rate=le32(r);fmt=(codec==0x270||(codec==0xfffe&&size>=40))&&channels>=1&&channels<=2&&sampleRate==44100;if(codec==0xfffe&&size>=40){r.seek(p+24);byte[] guid=new byte[16];r.readFully(guid);byte[] atracPlus={(byte)0xbf,(byte)0xaa,0x23,(byte)0xe9,0x58,(byte)0xcb,0x71,0x44,(byte)0xa1,0x19,(byte)0xff,(byte)0xfa,0x01,(byte)0xe4,(byte)0xce,0x62};fmt=fmt&&Arrays.equals(guid,atracPlus);}}else if(tag==0x64617461)data=size;else if(tag==0x66616374&&size>=4)fact=le32(r);r.seek(p+size+(size&1));}
  if(!fmt||data==0||rate==0||(fact>0?fact<=sampleRate*5:data<=rate*5))throw new IOException("Invalid ATRAC or track at most 5 seconds");}}
 void decode(File input,File wav)throws Exception{
  MediaExtractor ex=new MediaExtractor();MediaCodec codec=null;
  try(RandomAccessFile out=new RandomAccessFile(wav,"rw")){
   ex.setDataSource(input.getAbsolutePath());int idx=-1;MediaFormat fmt=null;
   for(int i=0;i<ex.getTrackCount();i++){MediaFormat t=ex.getTrackFormat(i);String m=t.getString(MediaFormat.KEY_MIME);if(m!=null&&m.startsWith("audio/")){idx=i;fmt=t;break;}}
   if(idx<0)throw new IOException("No supported audio track");ex.selectTrack(idx);codec=MediaCodec.createDecoderByType(fmt.getString(MediaFormat.KEY_MIME));codec.configure(fmt,null,null,0);codec.start();
   out.setLength(0);out.write(new byte[44]);boolean inEnd=false,end=false;MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();int sr=fmt.getInteger(MediaFormat.KEY_SAMPLE_RATE),ch=fmt.getInteger(MediaFormat.KEY_CHANNEL_COUNT),pcm=AudioFormat.ENCODING_PCM_16BIT;long samples=0,phase=0,last=System.nanoTime();byte[] bytes=new byte[65536];ByteArrayOutputStream batch=new ByteArrayOutputStream(65536);
   while(!end){check();if(System.nanoTime()-last>30000000000L)throw new IOException("Decoder timed out");
    if(!inEnd){int n=codec.dequeueInputBuffer(10000);if(n>=0){ByteBuffer b=codec.getInputBuffer(n);b.clear();int len=ex.readSampleData(b,0);if(len<0){codec.queueInputBuffer(n,0,0,0,MediaCodec.BUFFER_FLAG_END_OF_STREAM);inEnd=true;}else{codec.queueInputBuffer(n,0,len,Math.max(0,ex.getSampleTime()),0);ex.advance();}last=System.nanoTime();}}
    int n=codec.dequeueOutputBuffer(info,10000);
    if(n==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){MediaFormat o=codec.getOutputFormat();int ns=o.getInteger(MediaFormat.KEY_SAMPLE_RATE),nc=o.getInteger(MediaFormat.KEY_CHANNEL_COUNT);int np=o.containsKey(MediaFormat.KEY_PCM_ENCODING)?o.getInteger(MediaFormat.KEY_PCM_ENCODING):AudioFormat.ENCODING_PCM_16BIT;if(samples>0&&(ns!=sr||nc!=ch||np!=pcm))throw new IOException("Changing audio format not supported");sr=ns;ch=nc;pcm=np;}
    else if(n>=0){last=System.nanoTime();ByteBuffer b=codec.getOutputBuffer(n);if(info.size>0&&(info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){if(sr<8000||sr>192000||ch<1||ch>2||pcm!=AudioFormat.ENCODING_PCM_16BIT)throw new IOException("Unsupported decoded PCM format");b.position(info.offset);b.limit(info.offset+info.size);b.order(ByteOrder.LITTLE_ENDIAN);if(b.remaining()%(ch*2)!=0)throw new IOException("Unaligned PCM buffer");while(b.remaining()>=ch*2){short l=b.getShort(),r=ch==2?b.getShort():l;phase+=44100;while(phase>=sr){batch.write(l&255);batch.write((l>>8)&255);batch.write(r&255);batch.write((r>>8)&255);phase-=sr;samples++;if(samples>44100L*1800)throw new IOException("Track exceeds 30 minute alpha limit");}if(batch.size()>=bytes.length){batch.writeTo(new OutputStream(){public void write(int v)throws IOException{out.write(v);}public void write(byte[] a,int off,int len)throws IOException{out.write(a,off,len);}});batch.reset();}}}end=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;codec.releaseOutputBuffer(n,false);}
   }
   out.write(batch.toByteArray());if(samples<=44100*5)throw new IOException("GTA ignores tracks at most 5 seconds");long size=samples*4;out.seek(0);out.writeBytes("RIFF");w32(out,size+36);out.writeBytes("WAVEfmt ");w32(out,16);w16(out,1);w16(out,2);w32(out,44100);w32(out,176400);w16(out,4);w16(out,16);out.writeBytes("data");w32(out,size);
  }finally{if(codec!=null){try{codec.stop();}catch(Exception ignored){}codec.release();}ex.release();}
 }
 static void w16(RandomAccessFile f,int n)throws IOException{f.writeByte(n);f.writeByte(n>>8);}
 static void w32(RandomAccessFile f,long n)throws IOException{for(int i=0;i<4;i++)f.writeByte((int)(n>>(8*i)));}
}
