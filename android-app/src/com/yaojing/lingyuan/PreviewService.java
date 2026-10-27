package com.yaojing.lingyuan;

import android.app.*;
import android.content.*;
import android.os.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Keeps bundled resources available while a real WebGPU browser is foreground. */
public final class PreviewService extends Service {
    public static final String STOP="com.yaojing.lingyuan.STOP";
    private static final String CHANNEL="offline-preview";
    private static final int NOTICE=802;
    private final LocalBinder binder=new LocalBinder();
    private volatile AssetServer server;
    private volatile String failure;
    public final class LocalBinder extends Binder { public PreviewService service() { return PreviewService.this; } }
    @Override public void onCreate() {
        super.onCreate();
        NotificationManager manager=getSystemService(NotificationManager.class);
        manager.createNotificationChannel(new NotificationChannel(CHANNEL,"离线展示服务",NotificationManager.IMPORTANCE_LOW));
        startForeground(NOTICE,notification("正在准备离线资源"));
        try {
            final Map<String,Long> sizes=new HashMap<>();
            try (BufferedReader reader=new BufferedReader(new InputStreamReader(getAssets().open("web-inventory.tsv"),StandardCharsets.UTF_8))) {
                String line;while ((line=reader.readLine())!=null) { String[] fields=line.split("\t"); if (fields.length!=2) throw new IOException("资源清单格式错误");sizes.put(fields[0],Long.parseLong(fields[1])); }
            }
            server=new AssetServer(new AssetServer.Assets() {
                public InputStream open(String path) throws IOException { return getAssets().open("web/"+path); }
                public long length(String path) { Long size=sizes.get(path);return size==null?-1:size; }
            });
            manager.notify(NOTICE,notification("离线展示运行中；点击返回或停止"));
        } catch (IOException|RuntimeException error) {
            failure="离线资源启动失败，请重新打开应用。";manager.notify(NOTICE,notification(failure));
        }
    }
    private Notification notification(String text) {
        int flags=PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE;
        PendingIntent open=PendingIntent.getActivity(this,0,new Intent(this,LauncherActivity.class),flags);
        PendingIntent stop=PendingIntent.getService(this,1,new Intent(this,PreviewService.class).setAction(STOP),flags);
        return new Notification.Builder(this,CHANNEL).setSmallIcon(R.drawable.app_icon).setContentTitle("凌渊·人物与技能")
            .setContentText(text).setContentIntent(open).setOngoing(true).addAction(new Notification.Action.Builder(null,"停止",stop).build()).build();
    }
    public String url() { AssetServer active=server;return active==null?null:active.url(); }
    public String failure() { return failure; }
    @Override public IBinder onBind(Intent intent) { return binder; }
    @Override public int onStartCommand(Intent intent,int flags,int startId) {
        if (intent!=null && STOP.equals(intent.getAction())) { stopForeground(STOP_FOREGROUND_REMOVE);stopSelf(); }
        return START_NOT_STICKY;
    }
    @Override public void onDestroy() { AssetServer active=server;if (active!=null) active.close();server=null;super.onDestroy(); }
}
