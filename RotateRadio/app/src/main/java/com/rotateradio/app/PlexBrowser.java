package com.rotateradio.app;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.net.*;
import java.security.KeyStore;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;
import javax.net.ssl.HttpsURLConnection;

/** Plex Connect: read-only library browsing and authorized original-media downloads. */
final class PlexBrowser {
 final MainActivity a;
 final SharedPreferences prefs;
 final String client;
 final ExecutorService worker=Executors.newSingleThreadExecutor();
 static final String CLOUD="https://plex.tv", ALIAS="RotateRadio.Plex.v1";
 static final int PAGE=75, MAX=1000;
 String accountToken;
 Server server;
 long pinId;
 String pinCode;
 final LinkedHashMap<String,Entry> selected=new LinkedHashMap<>();
 PlexBrowser(MainActivity a){
  this.a=a;prefs=a.getSharedPreferences("plex",0);
  String id=prefs.getString("client",null);
  if(id==null){id=UUID.randomUUID().toString();prefs.edit().putString("client",id).apply();}
  client=id;accountToken=restore();
 }
 interface Work<T>{T run()throws Exception;}
 interface Result<T>{void accept(T value);}
 <T> void task(String title,Work<T> work,Result<T> result,Runnable back){
  if(a.isFinishing()||a.busy)return;
  ProgressDialog p=new ProgressDialog(a);p.setMessage(title);p.setCancelable(false);p.show();
  worker.submit(()->{try{T v=work.run();a.runOnUiThread(()->{if(a.isFinishing())return;p.dismiss();result.accept(v);});}
   catch(Exception e){String message=e instanceof PlexFailure?e.getMessage():"Connection or response failed ("+e.getClass().getSimpleName()+"). Check Plex remote access and internet.";a.runOnUiThread(()->{if(a.isFinishing())return;p.dismiss();new AlertDialog.Builder(a).setTitle("Plex Connect").setMessage(message).setPositiveButton("OK",(d,w)->{if(back!=null)back.run();}).show();});}});
 }
 static final class PlexFailure extends IOException{PlexFailure(String s){super(s);}}
 void show(){
  if(accountToken==null){new AlertDialog.Builder(a).setTitle("Plex Connect").setMessage("Sign in securely using Plex's own device-link page. You can authorize on your iPhone; RotateRadio never asks for your password. Your music is downloaded directly from your server.").setPositiveButton("Link Plex",(d,w)->link()).setNegativeButton("Cancel",null).show();}
  else if(server==null)servers();
  else home();
 }
 void link(){task("Requesting Plex link code…",()->jsonObject(CLOUD,"/api/v2/pins?strong=false",null,"POST"),j->{pinId=j.optLong("id");pinCode=j.optString("code");if(pinId<=0||pinCode.isEmpty()){error("Plex returned an invalid link code.",this::show);return;}pinDialog();},this::show);}
 void pinDialog(){new AlertDialog.Builder(a).setTitle("Plex link code: "+pinCode).setMessage("On your iPhone open https://plex.tv/link, sign in to Plex, and enter the code above. Then return here and press Check authorization.").setPositiveButton("Check authorization",(d,w)->checkPin()).setNeutralButton("Open Plex on handheld",(d,w)->{try{a.startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://plex.tv/link")));}catch(Exception ignored){}pinDialog();}).setNegativeButton("Cancel",null).show();}
 void checkPin(){task("Checking authorization…",()->jsonObject(CLOUD,"/api/v2/pins/"+pinId,null,"GET"),j->{String t=j.isNull("authToken")?"":j.optString("authToken");if(t.isEmpty()){if(j.optInt("expiresIn",1)<=0){error("Code expired. Request a new one.",this::link);}else{pinDialog();}return;}accountToken=t;store(t);servers();},this::pinDialog);}
 void error(String s,Runnable next){new AlertDialog.Builder(a).setTitle("Plex Connect").setMessage(s).setPositiveButton("OK",(d,w)->{if(next!=null)next.run();}).show();}
 javax.crypto.SecretKey key(boolean create)throws Exception{
  KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);
  if(ks.containsAlias(ALIAS))return (javax.crypto.SecretKey)ks.getKey(ALIAS,null);
  if(!create)throw new IOException("No saved key");
  KeyGenerator gen=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
  gen.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).setKeySize(256).build());return gen.generateKey();
 }
 void store(String token){try{Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,key(true));byte[] enc=c.doFinal(token.getBytes("UTF-8"));prefs.edit().putString("token",Base64.encodeToString(enc,Base64.NO_WRAP)).putString("iv",Base64.encodeToString(c.getIV(),Base64.NO_WRAP)).apply();}catch(Exception ignored){prefs.edit().remove("token").remove("iv").apply();}}
 String restore(){try{String t=prefs.getString("token",null),iv=prefs.getString("iv",null);if(t==null||iv==null)return null;Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,key(false),new GCMParameterSpec(128,Base64.decode(iv,Base64.NO_WRAP)));return new String(c.doFinal(Base64.decode(t,Base64.NO_WRAP)),"UTF-8");}catch(Exception e){return null;}}
 void signOut(){accountToken=null;server=null;selected.clear();prefs.edit().remove("token").remove("iv").apply();try{KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);ks.deleteEntry(ALIAS);}catch(Exception ignored){}show();}
 static class Server{String name,token,base;List<String> urls=new ArrayList<>();}
 static boolean approvedBase(String base){try{URL u=new URL(base);String h=u.getHost().toLowerCase(Locale.ROOT);return u.getProtocol().equals("https")&&u.getUserInfo()==null&&(h.equals("plex.tv")||h.endsWith(".plex.direct")||h.endsWith(".plex.tv"))&&(u.getPath().isEmpty()||u.getPath().equals("/"))&&u.getQuery()==null&&u.getRef()==null;}catch(Exception e){return false;}}
 void servers(){task("Discovering Plex servers…",()->{
  JSONArray rows=new JSONArray(requestText(CLOUD,"/api/v2/resources?includeHttps=1&includeRelay=1",accountToken,"GET",0,0));
  List<Server> out=new ArrayList<>();
  for(int i=0;i<rows.length();i++){JSONObject x=rows.getJSONObject(i);if(!Arrays.asList(x.optString("provides").split(",")).contains("server"))continue;Server s=new Server();s.name=x.optString("name","Plex server");s.token=x.isNull("accessToken")?"":x.optString("accessToken");if(s.token.isEmpty())continue;JSONArray con=x.optJSONArray("connections");if(con==null)continue;for(int pass=0;pass<3;pass++)for(int k=0;k<con.length();k++){JSONObject p=con.getJSONObject(k);boolean relay=p.optBoolean("relay"),local=p.optBoolean("local");if(pass==0&&(local||relay)||pass==1&&(!local||relay)||pass==2&&!relay)continue;String u=p.optString("uri");if(approvedBase(u)&&!s.urls.contains(u))s.urls.add(u.endsWith("/")?u.substring(0,u.length()-1):u);}if(!s.urls.isEmpty())out.add(s);}
  return out;
 },list->{if(list.isEmpty()){error("No accessible HTTPS Plex Media Server found. Check Remote Access and account permissions.",null);return;}String[] names=list.stream().map(x->x.name).toArray(String[]::new);new AlertDialog.Builder(a).setTitle("Choose Plex server").setItems(names,(d,w)->connect(list.get(w))).setNeutralButton("Sign out",(d,w)->signOut()).setNegativeButton("Close",null).show();},null);}
 void connect(Server s){task("Connecting to "+s.name+"…",()->{for(String base:s.urls){try{JSONObject m=jsonObject(base,"/library/sections",s.token,"GET");if(m.optJSONObject("MediaContainer")!=null){s.base=base;return s;}}catch(Exception ignored){}}throw new PlexFailure("No secure connection to this server. Check Plex Remote Access; a relay may restrict downloading.");},v->{server=v;selected.clear();home();},this::servers);}
 void home(){String[] options={"Music libraries","Music playlists","Install selected ("+selected.size()+")","Clear selection","Change server","Sign out"};new AlertDialog.Builder(a).setTitle("Plex · "+server.name).setItems(options,(d,w)->{switch(w){case 0:libraries();break;case 1:page("/playlists?playlistType=audio","Music playlists","playlist",0);break;case 2:installSelection();break;case 3:selected.clear();home();break;case 4:server=null;selected.clear();servers();break;case 5:signOut();break;}}).setNegativeButton("Close",null).show();}
 void libraries(){final Server s=server;task("Loading libraries…",()->{JSONObject m=container(s,"/library/sections",0,0);JSONArray dirs=m.optJSONArray("Directory");List<Entry> out=new ArrayList<>();if(dirs!=null)for(int i=0;i<dirs.length();i++){JSONObject j=dirs.getJSONObject(i);if(!"artist".equals(j.optString("type")))continue;String k=j.optString("key");if(k.matches("[0-9]+"))out.add(new Entry(k,j.optString("title","Music"),"","library"));}return out;},list->{if(list.isEmpty()){error("No music libraries available.",this::home);return;}new AlertDialog.Builder(a).setTitle("Music libraries").setItems(list.stream().map(x->x.title).toArray(String[]::new),(d,w)->library(list.get(w))).setNegativeButton("Back",(d,w)->home()).show();},this::home);}
 void library(Entry e){String root="/library/sections/"+e.id+"/all";String[] opts={"Artists","Albums","Tracks","Search tracks","Select entire library (up to 1000)"};new AlertDialog.Builder(a).setTitle(e.title).setItems(opts,(d,w)->{switch(w){case 0:page(root+"?type=8",e.title+" · Artists","artist",0);break;case 1:page(root+"?type=9",e.title+" · Albums","album",0);break;case 2:page(root+"?type=10",e.title+" · Tracks","track",0);break;case 3:EditText input=new EditText(a);input.setSingleLine();input.setHint("Song title");new AlertDialog.Builder(a).setTitle("Search tracks").setView(input).setPositiveButton("Search",(x,y)->page(root+"?type=10&title="+Uri.encode(input.getText().toString().trim()),"Search results","track",0)).setNegativeButton("Back",(x,y)->library(e)).show();break;case 4:collect(root+"?type=10",e.title);break;}}).setNegativeButton("Back",(d,w)->libraries()).show();}
 static class Entry{final String id,title,artist,type;Entry(String i,String t,String ar,String ty){id=i;title=t;artist=ar;type=ty;}String display(){return artist.isEmpty()?title:artist+" · "+title;}}
 static class Page{List<Entry> entries=new ArrayList<>();int count,total;}
 Page fetchPage(Server s,String path,String kind,int offset)throws Exception{
  JSONObject m=container(s,path,offset,PAGE);JSONArray arr=m.optJSONArray("Metadata");if(arr==null)arr=m.optJSONArray("Directory");
  Page p=new Page();p.count=arr==null?0:arr.length();p.total=m.optInt("totalSize",-1);
  if(arr!=null)for(int i=0;i<arr.length();i++){JSONObject j=arr.getJSONObject(i);String type=j.optString("type");if(kind.equals("playlist")){if(!"audio".equals(j.optString("playlistType")))continue;}else if(!kind.equals(type))continue;String id=j.optString("ratingKey");if(!id.matches("[0-9]+"))continue;String artist=kind.equals("track")?j.optString("grandparentTitle",j.optString("originalTitle","")):kind.equals("album")?j.optString("parentTitle"):"";p.entries.add(new Entry(id,j.optString("title","Untitled"),artist,kind));}return p;
 }
 boolean more(Page p,int offset){return p.count>0&&(p.total>=0?offset+p.count<p.total:p.count>=PAGE);}
 void page(String path,String title,String kind,int offset){Server s=server;task("Loading "+title+"…",()->fetchPage(s,path,kind,offset),p->{ArrayList<String> choices=new ArrayList<>();if(offset>0)choices.add("← Previous page");int begin=choices.size();for(Entry e:p.entries)choices.add((kind.equals("track")&&selected.containsKey(e.id)?"✓ ":"")+e.display());int end=choices.size();int next=-1,all=-1,install=-1;if(more(p,offset)){next=choices.size();choices.add("Next page →");}if(kind.equals("track")&&!p.entries.isEmpty()){all=choices.size();choices.add("Select all tracks in this collection");}install=choices.size();choices.add("Install selected ("+selected.size()+")");final int n=next,al=all,in=install;
  new AlertDialog.Builder(a).setTitle(title+" · "+(offset+1)+"–"+(offset+p.count)).setItems(choices.toArray(new String[0]),(d,w)->{if(w==n){page(path,title,kind,offset+p.count);return;}if(w==al){collect(path,title);return;}if(w==in){installSelection();return;}if(w<begin){page(path,title,kind,Math.max(0,offset-PAGE));return;}if(w>=end)return;Entry e=p.entries.get(w-begin);if(kind.equals("track")){if(selected.containsKey(e.id))selected.remove(e.id);else if(selected.size()<MAX)selected.put(e.id,e);else{error("Selection is limited to 1000 tracks.",this::home);return;}page(path,title,kind,offset);}else item(e,()->page(path,title,kind,offset));}).setNegativeButton("Home",(d,w)->home()).show();
 },this::home);}
 void item(Entry e,Runnable back){String trackPath=e.type.equals("playlist")?"/playlists/"+e.id+"/items":e.type.equals("artist")?"/library/metadata/"+e.id+"/allLeaves":"/library/metadata/"+e.id+"/children";List<String> options=new ArrayList<>();if(e.type.equals("artist"))options.add("Browse albums");options.add("Browse tracks");options.add("Select all tracks");new AlertDialog.Builder(a).setTitle(e.display()).setItems(options.toArray(new String[0]),(d,w)->{String op=options.get(w);if(op.equals("Browse albums"))page("/library/metadata/"+e.id+"/children",e.title+" · Albums","album",0);else if(op.equals("Browse tracks"))page(trackPath,e.title,"track",0);else collect(trackPath,e.title);}).setNegativeButton("Back",(d,w)->back.run()).show();}
 void collect(String path,String title){Server s=server;task("Selecting tracks · "+title+"…",()->{LinkedHashMap<String,Entry> batch=new LinkedHashMap<>();int offset=0;while(true){Page p=fetchPage(s,path,"track",offset);int old=batch.size();for(Entry e:p.entries)batch.put(e.id,e);if(batch.size()>MAX)throw new PlexFailure("Collection exceeds 1000 tracks. Select smaller albums or playlists.");if(!more(p,offset))break;if(batch.size()==old||offset>10000)throw new PlexFailure("Server pagination did not advance. Use smaller selections.");offset+=p.count;}return batch;},batch->{if(batch.isEmpty()){error("No audio tracks found.",this::home);return;}Set<String> combined=new HashSet<>(selected.keySet());combined.addAll(batch.keySet());if(combined.size()>MAX){error("Selection exceeds 1000 tracks. Install a smaller batch first.",this::home);return;}selected.putAll(batch);new AlertDialog.Builder(a).setTitle("Selected "+selected.size()+" tracks").setMessage("Download only when you press Install. Mobile data may be used.").setPositiveButton("Install now",(d,w)->installSelection()).setNegativeButton("Keep browsing",(d,w)->home()).show();},this::home);}
 void installSelection(){if(selected.isEmpty()){error("Select music first.",this::home);return;}final Server s=server;ArrayList<MainActivity.InputTrack> list=new ArrayList<>();for(Entry e:selected.values())list.add(new MainActivity.InputTrack(){public String name(){return e.display()+".audio";}public InputStream open()throws Exception{return openTrack(s,e);}});a.installPlex(list);}
 InputStream openTrack(Server s,Entry e)throws Exception{
  try{
   JSONObject m=container(s,"/library/metadata/"+e.id,0,0);JSONArray md=m.optJSONArray("Metadata");if(md==null||md.length()==0)throw new PlexFailure("Track unavailable");
   JSONObject j=md.getJSONObject(0);if(!"track".equals(j.optString("type")))throw new PlexFailure("Not an audio track");JSONArray media=j.optJSONArray("Media");String part=null;
   if(media!=null)for(int i=0;i<media.length()&&part==null;i++){JSONArray parts=media.getJSONObject(i).optJSONArray("Part");if(parts==null||parts.length()!=1)continue;String k=parts.getJSONObject(0).optString("key");if(k.startsWith("/library/parts/")&&!k.contains("..")&&!k.contains("?")&&!k.contains("#"))part=k;}
   if(part==null)throw new PlexFailure("No downloadable single-file audio source");HttpsURLConnection c=connection(s.base,part+"?download=1",s.token,"GET",0,0,"*/*");
   try{int code=c.getResponseCode();if(code!=200)throw new PlexFailure(code==401||code==403?"Plex denied download permission":"Plex download HTTP "+code);long len=c.getContentLengthLong();if(len>512L*1024*1024)throw new PlexFailure("Track exceeds 512 MB");String type=c.getContentType();if(type!=null&&(type.contains("text/html")||type.contains("application/json")||type.contains("xml")))throw new PlexFailure("Server returned a non-audio response");InputStream in=c.getInputStream();return new FilterInputStream(in){@Override public void close()throws IOException{try{super.close();}finally{c.disconnect();}}};}catch(Exception ex){c.disconnect();throw ex;}
  }catch(PlexFailure ex){throw ex;}catch(Exception ex){throw new PlexFailure("Plex track download failed ("+ex.getClass().getSimpleName()+")");}
 }
 JSONObject container(Server s,String path,int offset,int count)throws Exception{JSONObject j=new JSONObject(requestText(s.base,path,s.token,"GET",offset,count));JSONObject m=j.optJSONObject("MediaContainer");if(m==null)throw new PlexFailure("Invalid Plex media response");return m;}
 JSONObject jsonObject(String base,String path,String token,String method)throws Exception{return new JSONObject(requestText(base,path,token,method,0,0));}
 HttpsURLConnection connection(String base,String path,String token,String method,int offset,int count,String accept)throws Exception{
  if(!approvedBase(base)||!path.startsWith("/")||path.startsWith("//")||path.contains("\\")||path.contains("\r")||path.contains("\n"))throw new PlexFailure("Unsafe Plex endpoint");
  URL url=new URL(base+path);if(!url.getHost().equalsIgnoreCase(new URL(base).getHost()))throw new PlexFailure("Unsafe Plex host");HttpsURLConnection c=(HttpsURLConnection)url.openConnection();
  c.setInstanceFollowRedirects(false);c.setConnectTimeout(7000);c.setReadTimeout(20000);c.setRequestMethod(method);c.setRequestProperty("Accept",accept);c.setRequestProperty("X-Plex-Product","RotateRadio");c.setRequestProperty("X-Plex-Version","0.2.0");c.setRequestProperty("X-Plex-Platform","Android");c.setRequestProperty("X-Plex-Device","RG Rotate");c.setRequestProperty("X-Plex-Device-Name","RotateRadio");c.setRequestProperty("X-Plex-Client-Identifier",client);if(token!=null&&!token.isEmpty())c.setRequestProperty("X-Plex-Token",token);if(count>0){c.setRequestProperty("X-Plex-Container-Start",Integer.toString(offset));c.setRequestProperty("X-Plex-Container-Size",Integer.toString(count));}if(method.equals("POST")){c.setDoOutput(true);c.setFixedLengthStreamingMode(0);try(OutputStream o=c.getOutputStream()){} }return c;
 }
 String requestText(String base,String path,String token,String method,int offset,int count)throws Exception{HttpsURLConnection c=connection(base,path,token,method,offset,count,"application/json");try{int code=c.getResponseCode();if(code<200||code>=300)throw new PlexFailure(code==401||code==403?"Plex authorization denied. Sign out and link again if needed.":"Plex HTTP "+code);try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(out.size()+n>16*1024*1024)throw new PlexFailure("Plex response too large");out.write(b,0,n);}return out.toString("UTF-8");}}finally{c.disconnect();}}
}
