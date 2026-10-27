package com.yaojing.lingyuan;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.*;
import android.view.*;
import android.widget.*;

/** Native launcher for an honest offline WebGPU preview; never assumes WebView support. */
public final class LauncherActivity extends Activity {
    private final Handler handler=new Handler(Looper.getMainLooper());
    private PreviewService service;
    private boolean bound;
    private Button open;
    private TextView status;
    private final ServiceConnection connection=new ServiceConnection() {
        public void onServiceConnected(ComponentName name,IBinder binder) { service=((PreviewService.LocalBinder)binder).service();refresh(); }
        public void onServiceDisconnected(ComponentName name) { service=null;refresh(); }
    };
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(Color.rgb(7,23,37));getWindow().setNavigationBarColor(Color.rgb(7,23,37));
        ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(Color.rgb(7,23,37));
        LinearLayout column=new LinearLayout(this);column.setOrientation(LinearLayout.VERTICAL);column.setPadding(dp(28),dp(36),dp(28),dp(28));scroll.addView(column);
        text(column,"凌 渊",40,Color.rgb(229,206,148));
        text(column,"人物与三技能 · 交互展示",16,Color.rgb(155,181,192));
        text(column,"横屏查看角色与技能",24,Color.WHITE);
        text(column,"当前包含凌渊人物和三个技能的三维展示。人物和特效仍需精修，未包含完整游戏对局。",16,Color.rgb(185,202,208));
        text(column,"建议使用更新后的 Chrome 等浏览器横屏打开。网页优先使用 WebGPU，不可用时尝试 WebGL2；设备兼容性需要实际验证。",16,Color.rgb(185,202,208));
        text(column,"展示会在手机浏览器中运行，人物资源包含在应用内。使用时请保留离线服务；结束后可点击“停止并退出”。",15,Color.rgb(155,181,192));
        status=text(column,"正在准备离线资源…",15,Color.rgb(229,206,148));
        open=new Button(this);open.setText("打开角色展示");open.setEnabled(false);column.addView(open);open.setOnClickListener(v->launch());
        Button stop=new Button(this);stop.setText("停止并退出");column.addView(stop);
        stop.setOnClickListener(v->{stopService(new Intent(this,PreviewService.class));finish();});
        setContentView(scroll);
        if (Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},802);
    }
    private int dp(int n) { return (int)(n*getResources().getDisplayMetrics().density+.5f); }
    private TextView text(LinearLayout parent,String value,int size,int color) {
        TextView view=new TextView(this);view.setText(value);view.setTextSize(size);view.setTextColor(color);view.setPadding(0,dp(10),0,dp(16));view.setLineSpacing(dp(3),1);parent.addView(view);return view;
    }
    @Override public void onStart() {
        super.onStart();
        try {
            Intent intent=new Intent(this,PreviewService.class);startForegroundService(intent);bound=bindService(intent,connection,BIND_AUTO_CREATE);
        } catch (RuntimeException error) { status.setText("离线服务未能启动，请重新打开应用。"); }
    }
    private void refresh() {
        handler.removeCallbacksAndMessages(null);
        if (service!=null && service.failure()!=null) { status.setText(service.failure());open.setEnabled(false);return; }
        boolean ready=service!=null && service.url()!=null;
        status.setText(ready?"离线资源已就绪；浏览器将检查图形兼容性。":"正在准备离线资源…");open.setEnabled(ready);
        if (!ready) handler.postDelayed(this::refresh,500);
    }
    private void launch() {
        if (service==null || service.url()==null) { refresh();return; }
        Uri uri=Uri.parse(service.url()+"skill/index.html");Intent intent=new Intent(Intent.ACTION_VIEW,uri);intent.addCategory(Intent.CATEGORY_BROWSABLE);
        Intent chrome=new Intent(intent).setPackage("com.android.chrome");
        if (chrome.resolveActivity(getPackageManager())!=null) intent=chrome;
        Bundle extras=new Bundle();extras.putBinder("android.support.customtabs.extra.SESSION",null);intent.putExtras(extras);
        intent.putExtra("android.support.customtabs.extra.ENABLE_URLBAR_HIDING",true);
        intent.putExtra("android.support.customtabs.extra.TOOLBAR_COLOR",Color.rgb(7,23,37));
        try { startActivity(intent); }
        catch (ActivityNotFoundException missing) { status.setText("未找到可用浏览器。请安装或启用支持 WebGPU 的稳定版浏览器后重试。"); }
    }
    @Override public void onStop() {
        handler.removeCallbacksAndMessages(null);if (bound) { unbindService(connection);bound=false; }service=null;super.onStop();
    }
}
