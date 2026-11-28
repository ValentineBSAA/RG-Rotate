package com.rotateradio.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.content.res.ColorStateList;
import android.view.Gravity;
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
 final int BG=0xff101316, PANEL=0xff1b2229, TEXT=0xfff4f6fa, BLUE=0xff9cdbcb, MUTED=0xffa9b5bf;
 TextView headline, resultText, setupState; LinearLayout setup, sources, jobs, details; Button navHome,navJobs,navSettings,detectButton,inspectButton,autoButton; String saveId; boolean discovering; Button labButton; int pendingLab=-1; boolean labPlex=false; final String[] profileNames={"Official PPSSPP reference","ATRAC3 LP4 · 66 kbps","ATRAC3 LP2 · 132 kbps","ATRAC3+ · encoder default"}; final String[] profileArgs={"","atrac3-lp4","atrac3","atrac3plus"}; int screen=0;
 final String[] labels={"Liberty City Stories · USA/Korea","Liberty City Stories · Europe","Liberty City Stories · Germany","Liberty City Stories · Japan","Vice City Stories · USA","Vice City Stories · Europe","Vice City Stories · Germany","Vice City Stories · Japan","Both GTA games · USA"};
 final String[][] ids={{"ULUS10041"},{"ULES00151"},{"ULES00182"},{"ULJM05255"},{"ULUS10160"},{"ULES00502"},{"ULES00503"},{"ULJM05297"},{"ULUS10041","ULUS10160"}};
 Uri source, destination;
 TextView sourceText,destText,log,progressText;
 ProgressBar progress;
 Button start, cancel, sourceButton,destButton,plexButton;
 PlexBrowser plex;
 interface InputTrack { String name(); InputStream open() throws Exception; }
 Spinner game;
 final ExecutorService executor=Executors.newSingleThreadExecutor();
 final AtomicBoolean stopped=new AtomicBoolean();
 volatile Process encoder;
 boolean busy;
 int dp(float n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
 TextView txt(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
 GradientDrawable shape(int color,int radius){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));return d;}
 Button btn(String s,Runnable f){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(14);b.setTextColor(TEXT);b.setBackgroundTintList(ColorStateList.valueOf(0xff34444d));b.setMinHeight(dp(48));b.setOnClickListener(v->f.run());return b;}
 Button primary(String s,Runnable f){Button b=btn(s,f);b.setTextColor(0xff102822);b.setBackgroundTintList(new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},new int[]{0xff62746e,BLUE}));return b;}
 void add(LinearLayout l,View v){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(4),0,dp(4));l.addView(v,p);}
 LinearLayout column(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}
 LinearLayout card(LinearLayout l){LinearLayout c=column();c.setPadding(dp(13),dp(10),dp(13),dp(10));c.setBackground(shape(PANEL,18));add(l,c);return c;}
 TextView heading(String s){TextView t=txt(s,19,TEXT);t.setTypeface(null,Typeface.BOLD);return t;}
 void label(LinearLayout l,String s){add(l,txt(s,12,MUTED));}
 void nav(int index){screen=index;sources.setVisibility(index==0?View.VISIBLE:View.GONE);jobs.setVisibility(index==1?View.VISIBLE:View.GONE);setup.setVisibility(index==2?View.VISIBLE:View.GONE);headline.setText(index==0?"Your radio, your music":index==1?"Conversion queue":"Game & storage");Button[] buttons={navHome,navJobs,navSettings};for(int i=0;i<3;i++){buttons[i].setBackgroundTintList(ColorStateList.valueOf(i==index?0xff42685d:0xff283139));}}
 @Override public void onCreate(Bundle state){super.onCreate(state);
  source=load("source");destination=load("destination");saveId=getPreferences(0).getString("saveId",null);
  getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
  LinearLayout root=column();root.setBackgroundColor(BG);root.setPadding(dp(12),dp(6),dp(12),dp(6));setContentView(root);
  TextView brand=txt("ROTATE RADIO  /  0.3.3",12,BLUE);brand.setTypeface(null,Typeface.BOLD);add(root,brand);
  headline=heading("");add(root,headline);
  ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  LinearLayout body=column();scroll.addView(body);
  sources=column();jobs=column();setup=column();body.addView(sources);body.addView(jobs);body.addView(setup);
  plex=new PlexBrowser(this);
  LinearLayout welcome=card(sources);setupState=txt("",14,TEXT);add(welcome,setupState);add(welcome,btn("Game & storage settings",()->nav(2)));
  LinearLayout cloud=card(sources);add(cloud,heading("Plex music"));label(cloud,"Browse artists, albums, playlists or tracks.");plexButton=primary("Browse Plex",()->{if(!busy){labPlex=false;pendingLab=-1;if(destination==null){nav(2);line("Choose your PPSSPP folder first.");}else plex.show();}});add(cloud,plexButton);
  LinearLayout local=card(sources);add(local,heading("Music on this device"));sourceText=txt("",13,MUTED);add(local,sourceText);sourceButton=btn("Choose music folder",()->pick(11));add(local,sourceButton);start=primary("Convert & install folder",this::confirm);add(local,start);
  LinearLayout tips=card(sources);label(tips,"Close GTA before installing. Your original game files and existing tracks are kept.");
  LinearLayout job=card(jobs);add(job,heading("Batch progress"));progressText=txt("Ready for music",16,TEXT);add(job,progressText);
  progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setProgressTintList(ColorStateList.valueOf(BLUE));progress.setMax(1);add(job,progress);resultText=txt("No active batch",14,MUTED);add(job,resultText);
  cancel=btn("Cancel safely",()->{stopped.set(true);cancel.setEnabled(false);progressText.setText("Cancelling after safe cleanup…");Process p=encoder;if(p!=null)p.destroy();});cancel.setEnabled(false);add(job,cancel);
  details=card(jobs);Button toggle=btn("Show / hide activity details",()->log.setVisibility(log.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE));add(details,toggle);log=txt("No activity yet.",12,MUTED);log.setTextIsSelectable(true);log.setVisibility(View.GONE);add(details,log);
  LinearLayout target=card(setup);add(target,heading("PPSSPP destination"));label(target,"Automatically locate GTA saves on storage you have granted access to.");destText=txt("",13,MUTED);add(target,destText);autoButton=primary("Find PPSSPP automatically",()->discover(true));add(target,autoButton);destButton=btn("Grant SD card / folder access",()->pick(12));add(target,destButton);inspectButton=btn("Inspect installed tracks",this::inspectDestination);add(target,inspectButton);label(target,"In PPSSPP: Settings > System > PSP Memory Stick > Show Memory Stick folder. Select that exact folder.");
  LinearLayout games=card(setup);add(games,heading("Target game"));game=new Spinner(this);ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_item,labels);a.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);game.setAdapter(a);game.setSelection(Math.max(0,Math.min(labels.length-1,getPreferences(0).getInt("game",0))));add(games,game);
  game.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){public void onItemSelected(AdapterView<?> p,View v,int i,long id){getPreferences(0).edit().putInt("game",i).apply();refresh();}public void onNothingSelected(AdapterView<?> p){}});
  detectButton=btn("Detect game from saves",this::detectRegion);add(games,detectButton);label(games,"ATRAC3 LP4 • additive installation • experimental PSP radio");
  LinearLayout lab=card(setup);add(lab,heading("Audio compatibility"));label(lab,"Test one soundtrack at a time. Your existing music is preserved.");labButton=primary("Open compatibility lab",this::showLab);add(lab,labButton);add(setup,primary("Done",()->nav(0)));
  LinearLayout tabs=new LinearLayout(this);tabs.setOrientation(LinearLayout.HORIZONTAL);navHome=btn("Music",()->nav(0));navJobs=btn("Queue",()->nav(1));navSettings=btn("Setup",()->nav(2));for(Button button:new Button[]{navHome,navJobs,navSettings})tabs.addView(button,new LinearLayout.LayoutParams(0,dp(52),1));add(root,tabs);
  refresh();nav(destination==null?2:0);if(destination==null)discover(false);
 }
 @Override public void onBackPressed(){if(screen!=0){nav(0);return;}if(busy){nav(1);Toast.makeText(this,"Batch running. Cancel safely before exiting.",Toast.LENGTH_SHORT).show();return;}super.onBackPressed();}
 Uri load(String key){String x=getPreferences(0).getString(key,null);return x==null?null:Uri.parse(x);}
 void refresh(){sourceText.setText(source==null?"No music folder selected":shortUri(source));destText.setText(discovering?"Searching accessible storage…":destination==null?"No PPSSPP folder selected":saveId==null?shortUri(destination):saveId);setupState.setText(destination==null?"Setup needed · choose your PSP folder":"Destination selected · "+labels[game.getSelectedItemPosition() < 0 ? 0 : game.getSelectedItemPosition()]);start.setEnabled(!busy&&!discovering&&source!=null&&destination!=null);plexButton.setEnabled(!busy&&!discovering);destButton.setEnabled(!busy&&!discovering);sourceButton.setEnabled(!busy&&!discovering);game.setEnabled(!busy&&!discovering);if(autoButton!=null)autoButton.setEnabled(!busy&&!discovering);if(labButton!=null)labButton.setEnabled(!busy&&!discovering&&destination!=null);if(detectButton!=null)detectButton.setEnabled(!busy&&!discovering&&destination!=null);if(inspectButton!=null)inspectButton.setEnabled(!busy&&!discovering&&destination!=null);}
 String shortUri(Uri u){try{return DocumentsContract.getTreeDocumentId(u);}catch(Exception e){return u.toString();}}
 void pick(int req){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);if(req==12&&android.os.Build.VERSION.SDK_INT>=29){try{android.os.storage.StorageManager sm=(android.os.storage.StorageManager)getSystemService(STORAGE_SERVICE);for(android.os.storage.StorageVolume vol:sm.getStorageVolumes()){if(vol.isRemovable()&&android.os.Environment.MEDIA_MOUNTED.equals(vol.getState())){i=vol.createOpenDocumentTreeIntent();break;}}}catch(Exception ignored){}}i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);startActivityForResult(i,req);}
 @Override protected void onActivityResult(int r,int result,Intent i){super.onActivityResult(r,result,i);if(r==13){int profile=pendingLab;pendingLab=-1;if(result==RESULT_OK&&i!=null&&i.getData()!=null&&profile>0){Uri u=i.getData();startLab(profile,()->getContentResolver().openInputStream(u));}return;}if(result!=RESULT_OK||i==null||i.getData()==null)return;Uri u=i.getData();int flags=i.getFlags()&(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);try{getContentResolver().takePersistableUriPermission(u,flags);if(r==11){source=u;getPreferences(0).edit().putString("source",u.toString()).apply();refresh();}else if(r==12){if((flags&Intent.FLAG_GRANT_WRITE_URI_PERMISSION)==0)throw new IOException("Folder is read-only");discover(true,u); }}catch(Exception e){new AlertDialog.Builder(this).setMessage("Folder permission failed: "+e.getMessage()).setPositiveButton("OK",null).show();}}
 void detectRegion(){if(busy)return;if(destination==null){line("Choose PPSSPP folder first.");return;}Uri dst=destination;executor.submit(()->{try{D saves=saveDir(dst);Set<String> matches=new HashSet<>();for(D d:saves.children()){if(!d.dir())continue;String n=d.name.toUpperCase(Locale.ROOT);for(int i=0;i<8;i++)if(n.startsWith(ids[i][0]))matches.add(ids[i][0]);if(n.startsWith("ULJM05885"))matches.add("ULJM05255");if(n.startsWith("ULJM05884"))matches.add("ULJM05297");}int chosen=-1;if(matches.size()==1){for(int i=0;i<8;i++)if(matches.contains(ids[i][0]))chosen=i;}else if(matches.size()==2&&matches.contains("ULUS10041")&&matches.contains("ULUS10160"))chosen=8;int selection=chosen;runOnUiThread(()->{if(busy||!dst.equals(destination))return;if(selection>=0){game.setSelection(selection);line("Detected from save folders: "+labels[selection]+". Confirm your game before installation.");Toast.makeText(this,"Detected: "+labels[selection],Toast.LENGTH_LONG).show();}else {String message=matches.isEmpty()?"No recognized saves found. Select manually.":"Multiple regions found. Select manually.";line(message);Toast.makeText(this,message,Toast.LENGTH_LONG).show();}});}catch(Exception e){line("Detection failed: "+e.getMessage());runOnUiThread(()->Toast.makeText(this,"Detection failed. Check the selected folder.",Toast.LENGTH_LONG).show());}});}
 void confirm(){int target=game.getSelectedItemPosition();new AlertDialog.Builder(this).setTitle("Install station pack?").setMessage("Close GTA first. Tracks will be added to "+labels[target]+". No original files will be replaced. Try a folder with two tracks first.").setNegativeButton("Cancel",null).setPositiveButton("Install",(d,w)->runBatch(target)).show();}
 void line(String s){runOnUiThread(()->{String old=log.getText().toString();if(old.length()>14000)old=old.substring(old.length()-10000);log.setText(old+"\n"+s);});}
 void status(int done,int total,String s){runOnUiThread(()->{progress.setIndeterminate(false);progress.setMax(Math.max(1,total));progress.setProgress(done);progressText.setText(s);resultText.setText(done+" of "+total+" tracks processed");});}
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
 static final class Candidate {
  final Uri tree;final String id;final ArrayList<Integer> games;
  Candidate(Uri t,String i,ArrayList<Integer> g){tree=t;id=i;games=g;}
 }
 ArrayList<Integer> matchingGames(D d)throws IOException{ArrayList<Integer> out=new ArrayList<>();for(int i=0;i<8;i++)if(hasSave(d,ids[i][0]))out.add(i);if(out.contains(0)&&out.contains(4))out.add(8);return out;}
 void discover(boolean interactive){discover(interactive,null);}
 void discover(boolean interactive,Uri preferred){
  if(busy||discovering)return;discovering=true;refresh();
  executor.submit(()->{LinkedHashMap<String,Candidate> found=new LinkedHashMap<>();LinkedHashSet<Uri> grants=new LinkedHashSet<>();boolean[] limited={false};int[] examined={0};
   if(preferred!=null)grants.add(preferred);
   for(UriPermission p:getContentResolver().getPersistedUriPermissions())if(p.isReadPermission()&&p.isWritePermission()&&"com.android.externalstorage.documents".equals(p.getUri().getAuthority()))grants.add(p.getUri());
   for(Uri grant:grants){try{searchSaves(root(grant),0,new HashSet<>(),examined,found,limited);}catch(Exception e){limited[0]=true;}}
   ArrayList<Candidate> choices=new ArrayList<>(found.values());choices.sort(Comparator.comparing((Candidate c)->c.id.startsWith("primary:")).thenComparing(c->c.id));
   runOnUiThread(()->{discovering=false;refresh();if(isFinishing())return;
    if(choices.isEmpty()){if(interactive)new AlertDialog.Builder(this).setTitle("No GTA save folder found").setMessage("Grant access to the PSP or PPSSPP folder on your SD card. Save once inside GTA first. "+(limited[0]?"Some folders could not be fully searched.":"")).setPositiveButton("Choose SD folder",(x,y)->pick(12)).setNegativeButton("Cancel",null).show();return;}
    if(!interactive&&(choices.size()!=1||limited[0])){nav(2);return;}
    if(choices.size()==1&&!limited[0]){useCandidate(choices.get(0));return;}
    String[] names=choices.stream().map(c->c.id+" • "+labels[c.games.get(0)]).toArray(String[]::new);
    new AlertDialog.Builder(this).setTitle("Choose your PPSSPP folder").setItems(names,(x,y)->useCandidate(choices.get(y))).setNegativeButton("Cancel",null).setNeutralButton("Choose SD folder",(x,y)->pick(12)).show();
   });
  });
 }
 void searchSaves(D d,int depth,Set<String> seen,int[] examined,Map<String,Candidate> found,boolean[] limited)throws IOException{
  if(!d.dir()||!seen.add(d.id))return;
  if(++examined[0]>250){limited[0]=true;return;}
  if("SAVEDATA".equalsIgnoreCase(d.name)){ArrayList<Integer> matches=matchingGames(d);if(!matches.isEmpty())found.putIfAbsent(d.tree.getAuthority()+":"+d.id,new Candidate(d.tree,d.id,matches));return;}
  if(depth>=5)return;
  List<D> dirs=d.children();dirs.sort(Comparator.comparing((D x)->!x.name.equalsIgnoreCase("PSP")&&!x.name.equalsIgnoreCase("SAVEDATA")&&!x.name.toLowerCase(Locale.ROOT).contains("ppsspp")));
  for(D child:dirs){if(!child.dir())continue;String n=child.name.toLowerCase(Locale.ROOT);if(n.equals("android")||n.equals("roms")||n.equals("music")||n.equals("downloads")||n.equals("download")||n.equals("dcim")||n.equals("game")||n.equals("iso")||n.equals("system")||n.equals("textures")||n.equals("cheats")||n.equals("savestates")||n.equals("ppsspp_state"))continue;if(examined[0]>=250){limited[0]=true;break;}try{searchSaves(child,depth+1,seen,examined,found,limited);}catch(Exception e){limited[0]=true;}}
 }
 void useCandidate(Candidate c){if(busy||discovering)return;destination=c.tree;saveId=c.id;getPreferences(0).edit().putString("destination",c.tree.toString()).putString("saveId",c.id).apply();int selected=game.getSelectedItemPosition();if(!c.games.contains(selected)&&c.games.size()==1)game.setSelection(c.games.get(0));else if(!c.games.contains(selected)){String[] names=c.games.stream().map(i->labels[i]).toArray(String[]::new);new AlertDialog.Builder(this).setTitle("Choose GTA game").setItems(names,(x,y)->game.setSelection(c.games.get(y))).setNegativeButton("Later",null).show();}refresh();Toast.makeText(this,"GTA save folder detected. Confirm it matches PPSSPP.",Toast.LENGTH_LONG).show();}
 D saveDir(Uri t)throws IOException{if(t!=null&&t.equals(destination)&&saveId!=null){D resolved=new D(t,saveId,"SAVEDATA",Document.MIME_TYPE_DIR);try(Cursor c=getContentResolver().query(resolved.uri,new String[]{Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE},null,null,null)){if(c==null||!c.moveToFirst()||!"SAVEDATA".equalsIgnoreCase(c.getString(0))||!Document.MIME_TYPE_DIR.equals(c.getString(1)))throw new IOException("Detected save folder unavailable; run automatic discovery again");}return resolved;}D r=root(t);if(!r.dir())throw new IOException("Selected item is not a directory");if("SAVEDATA".equalsIgnoreCase(r.name))return r;D p="PSP".equalsIgnoreCase(r.name)?r:r.child("PSP");if(p==null||!p.dir())throw new IOException("Select the existing PSP or SAVEDATA folder");D s=p.child("SAVEDATA");if(s==null||!s.dir())throw new IOException("Existing SAVEDATA not found. Start PPSSPP first.");return s;}
 boolean hasSave(D saves,String target)throws IOException{
  for(D x:saves.children()){if(!x.dir())continue;String n=x.name.toUpperCase(Locale.ROOT);if(n.endsWith("CUSTOMTRACKS"))continue;boolean match=n.startsWith(target)||(target.equals("ULJM05255")&&n.startsWith("ULJM05885"))||(target.equals("ULJM05297")&&n.startsWith("ULJM05884"));if(match){D param=x.child("PARAM.SFO");if(param!=null&&!param.dir())return true;}}return false;
 }
 void inspectDestination(){if(busy||destination==null)return;Uri dst=destination;int target=game.getSelectedItemPosition();if(target<0)return;inspectButton.setEnabled(false);executor.submit(()->{
  StringBuilder report=new StringBuilder();try{D saves=saveDir(dst);report.append("Storage provider: ").append(dst.getAuthority()).append("\nSAVEDATA document: ").append(saves.id).append("\n");
  for(String id:ids[target]){report.append("\n").append(id).append(" • matching game save: ").append(hasSave(saves,id)?"found":"NOT FOUND").append("\n");D dir=saves.child(id+"CUSTOMTRACKS");if(dir==null||!dir.dir()){report.append("Custom tracks folder missing\n");continue;}report.append("Folder: ").append(dir.id).append("\n");int count=0;for(D file:dir.children()){if(file.dir())continue;boolean valid=file.name.toLowerCase(Locale.ROOT).endsWith(".gta");if(valid)count++;if(count<=60&&report.length()<16000){report.append(file.name);try(InputStream in=getContentResolver().openInputStream(file.uri)){report.append(in!=null&&in.read()!=-1?" • readable":" • empty/unreadable");}catch(Exception e){report.append(" • unreadable");}report.append("\n");}}report.append("Total .gta files: ").append(count).append("\n");}
  report.append("\nCompare this location with PPSSPP's active Memory Stick folder. Files present does not prove in-game playback.");}catch(Exception e){report.append("\nInspection failed: ").append(e.getMessage());}String result=report.toString();runOnUiThread(()->{refresh();if(isFinishing())return;TextView t=txt(result,13,TEXT);t.setTextIsSelectable(true);t.setPadding(dp(14),dp(8),dp(14),dp(8));ScrollView sc=new ScrollView(this);sc.addView(t);new AlertDialog.Builder(this).setTitle("Destination inspection").setView(sc).setPositiveButton("Done",null).setNeutralButton("Copy report",(dialog,which)->{android.content.ClipboardManager cm=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);cm.setPrimaryClip(ClipData.newPlainText("RotateRadio destination",result));}).show();});});
 }
 boolean supported(String n){return n.toLowerCase(Locale.ROOT).matches(".*\\.(mp3|m4a|aac|wav|flac|ogg|opus|at3|gta)$");}
 void scan(D d,List<D> out,int depth,Set<String> seen)throws IOException{check();if(depth>20||!seen.add(d.id))return;for(D x:d.children()){if(x.dir())scan(x,out,depth+1,seen);else if(supported(x.name)){if(out.size()>=1000)throw new IOException("Folder exceeds 1000 supported files; split it into smaller packs");out.add(x);}}}
 void runBatch(int target){runBatch(target,null);}
 void installPlex(List<InputTrack> tracks){if(busy||discovering)return;if(labPlex){if(tracks.size()!=1){new AlertDialog.Builder(this).setTitle("Select exactly one song").setMessage("Clear the Plex selection and choose a single song for this compatibility test.").setPositiveButton("OK",(x,y)->plex.show()).setNegativeButton("Cancel",(x,y)->{labPlex=false;pendingLab=-1;}).show();return;}int p=pendingLab;labPlex=false;pendingLab=-1;if(p>0)startLab(p,()->tracks.get(0).open());return;}if(destination==null){new AlertDialog.Builder(this).setMessage("Choose your PPSSPP PSP or SAVEDATA folder first, then return to Plex Connect.").setPositiveButton("OK",null).show();return;}int target=game.getSelectedItemPosition();new AlertDialog.Builder(this).setTitle("Install "+tracks.size()+" Plex tracks?").setMessage("Download, convert and add to "+labels[target]+". Close GTA first. Your Plex library and original game files will not be modified.").setNegativeButton("Cancel",null).setPositiveButton("Install",(d,w)->runBatch(target,tracks)).show();}
 void runBatch(int target,List<InputTrack> plexTracks){if(busy||discovering)return;busy=true;autoButton.setEnabled(false);nav(1);progress.setIndeterminate(true);progressText.setText("Preparing your batch…");resultText.setText("Scanning music and checking destination");detectButton.setEnabled(false);inspectButton.setEnabled(false);getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);plexButton.setEnabled(false);stopped.set(false);start.setEnabled(false);cancel.setEnabled(true);sourceButton.setEnabled(false);destButton.setEnabled(false);game.setEnabled(false);getPreferences(0).edit().putInt("game",target).apply();Uri src=source,dst=destination;log.setText("Scanning...");executor.submit(()->{int ok=0,fail=0,skip=0;try{
  D s=saveDir(dst);line("Actual SAVEDATA: "+s.id+" / "+dst.getAuthority());for(String id:ids[target])if(!hasSave(s,id))throw new IOException("No matching "+id+" game save found here. Save in GTA normally, then select the exact PPSSPP Memory Stick folder and correct region.");List<InputTrack> tracks=new ArrayList<>();if(plexTracks!=null){tracks.addAll(plexTracks);}else{D input=root(src);
  // Never scan a destination tree, which may contain game saves.
  if(src.equals(dst)||input.id.equals(s.id)||(src.getAuthority().equals(dst.getAuthority())&&(s.id.startsWith(input.id+"/")||input.id.startsWith(s.id+"/")||input.id.endsWith(":")&&s.id.startsWith(input.id)))||input.id.toLowerCase(Locale.ROOT).endsWith(":psp")||input.name.equalsIgnoreCase("PSP")||input.name.equalsIgnoreCase("SAVEDATA"))throw new IOException("Choose a separate music folder, not PPSSPP data.");
  List<D> local=new ArrayList<>();scan(input,local,0,new HashSet<>());for(D doc:local)tracks.add(new InputTrack(){public String name(){return doc.name;}public InputStream open()throws Exception{return getContentResolver().openInputStream(doc.uri);}});}if(tracks.isEmpty())throw new IOException("No supported music files found");
  List<D> outputs=new ArrayList<>();for(String id:ids[target]){if(s.child(id+"CUSTOMTRACKS_RR_BACKUP")!=null)throw new IOException("Compatibility test is active for "+id+". Restore original tracks in Setup first.");D folder=s.mkdir(id+"CUSTOMTRACKS");outputs.add(folder);line("Output folder: "+folder.id);}
  for(int i=0;i<tracks.size();i++){check();InputTrack track=tracks.get(i);String trackName=track.name();status(i,tracks.size(),(plexTracks!=null?"Downloading ":"Track ")+(i+1)+"/"+tracks.size()+": "+trackName);
   File raw=File.createTempFile("rr-input-",".tmp",getCacheDir()),wav=null,at3=null;
   try{try(InputStream in=track.open();OutputStream out=new FileOutputStream(raw)){if(in==null)throw new IOException("Cannot open input");copy(in,out,512L*1024*1024);}
    status(i,tracks.size(),"Converting "+(i+1)+"/"+tracks.size()+": "+trackName);String lower=trackName.toLowerCase(Locale.ROOT);File ready;
    if(lower.endsWith(".at3")||lower.endsWith(".gta")){ready=raw;}else{wav=File.createTempFile("rr-pcm-",".wav",getCacheDir());decode(raw,wav);check();at3=File.createTempFile("rr-atrac-",".at3",getCacheDir());int chosen=getPreferences(0).getInt("codec_"+target,1);if(chosen<1||chosen>3)chosen=1;encode(wav,at3,chosen);ready=at3;}
    status(i,tracks.size(),"Verifying and installing "+(i+1)+"/"+tracks.size()+": "+trackName);validateAtrac(ready);String hash=sha(ready);String base=trackName.replaceFirst("\\.[^.]+$","").replaceAll("[^A-Za-z0-9 _.-]","_");if(base.length()>48)base=base.substring(0,48);String name="RR-"+hash.substring(0,16)+"-"+base+".gta";boolean added=false;
    for(D dest:outputs){check();D exists=null;for(D candidate:dest.children()){if(candidate.name.startsWith("RR-"+hash.substring(0,16)+"-")&&candidate.name.endsWith(".gta")){try(InputStream prior=getContentResolver().openInputStream(candidate.uri)){if(prior!=null&&hash.equals(sha(prior))){exists=candidate;break;}}}}if(exists!=null){line("Already verified: "+exists.id);continue;}if(dest.child(name)!=null)throw new IOException("Filename collision; existing file kept");install(ready,dest,name,hash);added=true;}
    if(added){ok++;line("Installed: "+trackName);}else skip++;
   }catch(Exception e){if(stopped.get())throw e;fail++;line("FAILED "+trackName+": "+e.getMessage());}finally{raw.delete();if(wav!=null)wav.delete();if(at3!=null)at3.delete();}
  status(i+1,tracks.size(),"Processed "+(i+1)+" of "+tracks.size()+": "+trackName);
  }status(tracks.size(),tracks.size(),fail==0?"Batch complete":"Batch complete with errors");String summary="Files verified: "+ok+" new · "+skip+" existing · "+fail+" failed";line(summary);runOnUiThread(()->resultText.setText(summary+"\nGTA playback not verified. Use Setup > Inspect installed tracks."));
 }catch(Exception e){String message=stopped.get()?"Cancelled safely":"Batch stopped";String summary="Installed "+ok+" · Already present "+skip+" · Failed "+fail;line("Stopped: "+e.getMessage()+" (completed tracks kept)");runOnUiThread(()->{progress.setIndeterminate(false);progressText.setText(message);resultText.setText(summary+" · Completed tracks kept");});}finally{runOnUiThread(()->{getWindow().clearFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);busy=false;cancel.setEnabled(false);sourceButton.setEnabled(true);destButton.setEnabled(true);game.setEnabled(true);refresh();});}});}
 void copy(InputStream in,OutputStream out,long limit)throws Exception{byte[] b=new byte[65536];int n;long total=0;while((n=in.read(b))!=-1){check();total+=n;if(total>limit)throw new IOException("File exceeds safety limit");out.write(b,0,n);}}
 String sha(File f)throws Exception{try(InputStream in=new FileInputStream(f)){return sha(in);}}
 String sha(InputStream in)throws Exception{MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1){check();d.update(b,0,n);}StringBuilder s=new StringBuilder();for(byte x:d.digest())s.append(String.format(Locale.ROOT,"%02x",x&255));return s.toString();}
 void install(File f,D dest,String name,String digest)throws Exception{
  Uri tmp=DocumentsContract.createDocument(getContentResolver(),dest.uri,"application/octet-stream","RR-stage-"+UUID.randomUUID()+".part");if(tmp==null)throw new IOException("Cannot create staging file");boolean committed=false;
  try{try(InputStream in=new FileInputStream(f);OutputStream out=getContentResolver().openOutputStream(tmp,"w")){if(out==null)throw new IOException("Cannot write staging file");copy(in,out,512L*1024*1024);}
   try(InputStream in=getContentResolver().openInputStream(tmp)){if(in==null||!digest.equals(sha(in)))throw new IOException("Copy checksum mismatch");}
   check();if(dest.child(name)!=null)throw new IOException("Existing file kept");Uri fin=DocumentsContract.renameDocument(getContentResolver(),tmp,name);if(fin==null)throw new IOException("Provider cannot rename safely");committed=true;D installed=dest.child(name);if(installed==null||installed.dir())throw new IOException("Final filename not found after rename; inspect "+dest.id);try(InputStream in=getContentResolver().openInputStream(installed.uri)){if(in==null||!digest.equals(sha(in)))throw new IOException("Final file checksum mismatch: "+installed.id);}line("Verified file: "+installed.id);
  }finally{if(!committed)try{DocumentsContract.deleteDocument(getContentResolver(),tmp);}catch(Exception ignored){}}
 }
 void encode(File wav,File out,int profile)throws Exception{
  File bin=new File(getApplicationInfo().nativeLibraryDir,"libatracdenc.so");if(!bin.canExecute())throw new IOException("Native encoder unavailable");
  Process p=new ProcessBuilder(bin.getAbsolutePath(),"-e",profileArgs[profile],"--container","riff","-i",wav.getAbsolutePath(),"-o",out.getAbsolutePath()).redirectErrorStream(true).start();encoder=p;
  try{ByteArrayOutputStream tail=new ByteArrayOutputStream();try(InputStream in=p.getInputStream()){byte[] b=new byte[2048];int n;while((n=in.read(b))!=-1){check();if(tail.size()>6000)tail.reset();tail.write(b,0,n);}}int exit=p.waitFor();check();if(exit!=0)throw new IOException("ATRAC encoder exit "+exit+": "+tail.toString("UTF-8"));}finally{p.destroy();encoder=null;}
 }
 interface LabInput {InputStream open()throws Exception;}
 String labKey(int target){return "lab_"+target;}
 void showLab(){
  if(busy||discovering||destination==null)return;int target=game.getSelectedItemPosition();
  if(target<0||target>=8){new AlertDialog.Builder(this).setMessage("Choose one GTA game (not Both) in Setup before testing.").setPositiveButton("OK",null).show();return;}
  String recorded=getPreferences(0).getString(labKey(target),"No playback result recorded");
  int preferred=getPreferences(0).getInt("codec_"+target,1);if(preferred<1||preferred>3)preferred=1;
  String[] options={"1 · Install official reference track","2 · Test a song with an encoding profile","3 · Restore original soundtrack","4 · Record playback result / select preferred codec"};
  new AlertDialog.Builder(this).setTitle("Audio compatibility lab").setItems(options,(x,y)->{if(y==0)confirmLab(0);else if(y==1)new AlertDialog.Builder(this).setTitle("Choose encoding").setItems(Arrays.copyOfRange(profileNames,1,4),(z,k)->confirmLab(k+1)).setNegativeButton("Back",(z,k)->showLab()).show();else if(y==2)new AlertDialog.Builder(this).setTitle("Restore original soundtrack?").setMessage("Completely close GTA first. Test music will be archived, not deleted.").setPositiveButton("Restore",(z,k)->restoreLab()).setNegativeButton("Cancel",null).show();else recordLab(target);}).setMessage(null).setNegativeButton("Close",null).setNeutralButton("Results",(x,y)->new AlertDialog.Builder(this).setTitle("Last reported result").setMessage(recorded+"\nImport profile: "+profileNames[getPreferences(0).getInt("codec_"+target,1)]).setPositiveButton("OK",null).show()).show();
 }
 void confirmLab(int profile){new AlertDialog.Builder(this).setTitle(profileNames[profile]).setMessage("Completely close GTA / PPSSPP first. The existing CUSTOMTRACKS folder will be renamed to a backup next to it. Only one test track will be active. Restore original soundtrack afterward. No saves or music will be deleted.").setPositiveButton("Continue",(x,y)->{if(profile==0){startLab(0,this::referenceTrack);return;}new AlertDialog.Builder(this).setTitle("Choose one test song").setItems(new String[]{"Plex (select exactly one track)","Local audio file"},(z,k)->{pendingLab=profile;if(k==0){labPlex=true;plex.selected.clear();plex.show();}else{labPlex=false;Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("*/*");i.addCategory(Intent.CATEGORY_OPENABLE);i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivityForResult(i,13);}}).setNegativeButton("Cancel",null).show();}).setNegativeButton("Cancel",null).show();}
 InputStream referenceTrack()throws Exception{
  java.net.URL url=new java.net.URL("https://www.ppsspp.org/static/img/docs/custom_background_music/We_Wish_You_a_Merry_Christmas.at3");
  javax.net.ssl.HttpsURLConnection c=(javax.net.ssl.HttpsURLConnection)url.openConnection();c.setConnectTimeout(10000);c.setReadTimeout(20000);c.setInstanceFollowRedirects(false);
  try{if(c.getResponseCode()!=200)throw new IOException("Reference download HTTP "+c.getResponseCode());if(c.getContentLengthLong()>32L*1024*1024)throw new IOException("Reference exceeds size limit");return new FilterInputStream(c.getInputStream()){public void close()throws IOException{try{super.close();}finally{c.disconnect();}}};}catch(Exception e){c.disconnect();throw e;}
 }
 void renameFolder(D parent,D child,String name)throws Exception{
  if(child==null||!child.dir()||parent.child(name)!=null)throw new IOException("Cannot safely rename folder to "+name);
  Uri result=DocumentsContract.renameDocument(getContentResolver(),child.uri,name);if(result==null)throw new IOException("Storage provider refused rename");
  D check=parent.child(name);if(check==null||!check.dir()||parent.child(child.name)!=null)throw new IOException("Folder rename could not be verified. Inspect storage before continuing.");
 }
 void archiveTest(D saves,D active,String id)throws Exception{if(active!=null)renameFolder(saves,active,id+"CUSTOMTRACKS_RR_TEST_"+UUID.randomUUID().toString().substring(0,8));}
 void labBegin(String title){busy=true;stopped.set(false);nav(1);log.setText(title);progress.setIndeterminate(true);progressText.setText(title);resultText.setText("One-track compatibility test");cancel.setEnabled(true);refresh();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);}
 void labEnd(String title,String message){runOnUiThread(()->{busy=false;cancel.setEnabled(false);progress.setIndeterminate(false);progressText.setText(title);resultText.setText(message);getWindow().clearFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);refresh();});}
 void startLab(int profile,LabInput input){
  if(busy||discovering||destination==null||profile<0||profile>3)return;int target=game.getSelectedItemPosition();if(target<0||target>=8)return;Uri dst=destination;String id=ids[target][0];labBegin("Preparing "+profileNames[profile]);
  executor.submit(()->{File raw=null,wav=null,at3=null;try{
   D saves=saveDir(dst);if(!hasSave(saves,id))throw new IOException("Matching save not found. Confirm active PPSSPP folder.");
   raw=File.createTempFile("rr-lab-input-",".tmp",getCacheDir());try(InputStream in=input.open();OutputStream out=new FileOutputStream(raw)){if(in==null)throw new IOException("Cannot read test source");copy(in,out,profile==0?32L*1024*1024:512L*1024*1024);}
   File ready=raw;if(profile!=0){status(0,1,"Encoding "+profileNames[profile]);wav=File.createTempFile("rr-lab-pcm-",".wav",getCacheDir());decode(raw,wav);check();at3=File.createTempFile("rr-lab-output-",".at3",getCacheDir());encode(wav,at3,profile);ready=at3;}
   validateAtrac(ready);String hash=sha(ready);line("Test RIFF: "+atracInfo(ready));check();
   String activeName=id+"CUSTOMTRACKS",backupName=activeName+"_RR_BACKUP";D active=saves.child(activeName),backup=saves.child(backupName);
   if(backup==null){if(active==null)active=saves.mkdir(activeName);renameFolder(saves,active,backupName);line("Original music backed up: "+backupName);}else{if(!backup.dir())throw new IOException("Backup name collision");archiveTest(saves,active,id);}
   D test=saves.mkdir(activeName);install(ready,test,"RRTEST.gta",hash);check();getPreferences(0).edit().putInt("lab_active_"+target,profile).putString(labKey(target),profileNames[profile]+" installed · awaiting in-game test").apply();
   status(1,1,"Test track verified");labEnd("Test ready","Launch GTA, enable Custom Tracks and drive for 30 seconds. Return to Setup > Audio compatibility to record the result or restore.");
  }catch(Exception e){line("Lab error: "+e.getMessage());labEnd(stopped.get()?"Test cancelled":"Test not ready",e.getMessage()+" · Original music is preserved; use Restore original soundtrack if a backup was created.");}finally{if(raw!=null)raw.delete();if(wav!=null)wav.delete();if(at3!=null)at3.delete();}});
 }
 String atracInfo(File f)throws IOException{try(RandomAccessFile r=new RandomAccessFile(f,"r")){r.seek(12);while(r.getFilePointer()+8<=r.length()){int tag=r.readInt();long size=le32(r),p=r.getFilePointer();if(size>r.length()-p)break;if(tag==0x666d7420&&size>=16){int codec=le16(r),channels=le16(r);long sample=le32(r),bytes=le32(r);int block=le16(r);return "codec 0x"+Integer.toHexString(codec)+" / "+channels+" ch / "+sample+" Hz / "+bytes*8+" bps / frame "+block+" bytes";}r.seek(p+size+(size&1));}}return "fmt chunk unavailable";}
 void restoreLab(){if(busy||discovering||destination==null)return;int target=game.getSelectedItemPosition();if(target<0||target>=8)return;Uri dst=destination;String id=ids[target][0];labBegin("Restoring original soundtrack");cancel.setEnabled(false);executor.submit(()->{try{D saves=saveDir(dst);String active=id+"CUSTOMTRACKS";D backup=saves.child(active+"_RR_BACKUP");if(backup==null){labEnd("No backup found","Nothing was changed.");return;}if(!backup.dir())throw new IOException("Backup is not a folder");archiveTest(saves,saves.child(active),id);renameFolder(saves,backup,active);getPreferences(0).edit().remove("lab_active_"+target).apply();labEnd("Original soundtrack restored","Test files archived beside CUSTOMTRACKS. No music deleted.");}catch(Exception e){labEnd("Restore needs attention",e.getMessage()+" · Do not delete the backup folder.");}});}
 void recordLab(int target){int profile=getPreferences(0).getInt("lab_active_"+target,-1);if(profile<0||profile>3){new AlertDialog.Builder(this).setMessage("Install and test one profile first.").setPositiveButton("OK",null).show();return;}new AlertDialog.Builder(this).setTitle(profileNames[profile]).setItems(new String[]{"Played for at least 30 seconds","Unavailable / skipped / no sound"},(x,y)->{getPreferences(0).edit().putString(labKey(target),profileNames[profile]+(y==0?" · user reported playback":" · user reported failure")).apply();if(y==0&&profile>0)new AlertDialog.Builder(this).setTitle("Use this profile for future imports?").setMessage("Your physical-device test is the basis for this choice. Existing files will not be changed.").setPositiveButton("Use profile",(z,k)->getPreferences(0).edit().putInt("codec_"+target,profile).apply()).setNegativeButton("Not now",null).show();}).setNegativeButton("Cancel",null).show();}
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
