package com.yaojing.lingyuan;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

/** Bounded, read-only loopback HTTP server for the APK's offline web assets. */
public final class AssetServer implements Closeable {
    public interface Assets {
        InputStream open(String path) throws IOException;
        long length(String path);
    }
    private final Assets assets;
    private final ServerSocket socket;
    private final String prefix;
    private final ThreadPoolExecutor workers;
    private final Set<Socket> clients = Collections.newSetFromMap(new ConcurrentHashMap<Socket, Boolean>());
    private volatile boolean closed;
    public AssetServer(Assets assets) throws IOException {
        this.assets = assets;
        socket = new ServerSocket();
        socket.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), 0), 8);
        prefix = "/session/" + UUID.randomUUID().toString().replace("-", "") + "/";
        workers = new ThreadPoolExecutor(2, 2, 15, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(8));
        workers.allowCoreThreadTimeOut(true);
        Thread accept = new Thread(() -> {
            while (!closed) {
                try {
                    final Socket client = socket.accept();
                    clients.add(client);
                    client.setSoTimeout(5000);
                    try { workers.execute(() -> serve(client)); }
                    catch (RejectedExecutionException full) { clients.remove(client); client.close(); }
                } catch (IOException error) { if (!closed) close(); }
            }
        }, "yaojing-loopback");
        accept.setDaemon(true); accept.start();
    }
    public String url() { return "http://127.0.0.1:" + socket.getLocalPort() + prefix; }
    public int port() { return socket.getLocalPort(); }
    private static String line(InputStream input) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        for (int count = 0; count < 8192; count++) {
            int b = input.read();
            if (b == -1) throw new EOFException();
            if (b == '\n') return new String(buffer.toByteArray(), StandardCharsets.US_ASCII).replace("\r", "");
            buffer.write(b);
        }
        throw new IOException("Request line too large");
    }
    private void serve(Socket client) {
        try (Socket connection = client) {
            InputStream input = connection.getInputStream(); OutputStream output = connection.getOutputStream();
            String[] request = line(input).split(" ");
            if (request.length != 3 || !request[1].startsWith("/")) { error(output,400,"Bad request",null); return; }
            Map<String,String> headers = new HashMap<>();
            for (int count = 0; ; count++) {
                String row = line(input); if (row.isEmpty()) break;
                if (count >= 48) { error(output,431,"Too many headers",null); return; }
                int colon = row.indexOf(':'); if (colon <= 0) { error(output,400,"Bad header",null); return; }
                String key = row.substring(0,colon).toLowerCase(Locale.ROOT);
                if (headers.put(key,row.substring(colon+1).trim()) != null) { error(output,400,"Duplicate header",null); return; }
            }
            String expected = "127.0.0.1:" + port();
            if (!expected.equals(headers.get("host"))) { error(output,403,"Invalid host",null); return; }
            boolean head = request[0].equals("HEAD");
            if (!head && !request[0].equals("GET")) { error(output,405,"Read only","Allow: GET, HEAD\r\n"); return; }
            final String path;
            try { path = new URI(request[1]).getPath(); }
            catch (URISyntaxException bad) { error(output,400,"Invalid path",null); return; }
            if (path == null || path.indexOf('\0') >= 0 || path.indexOf('\\') >= 0 || Arrays.asList(path.split("/",-1)).contains("..")) {
                error(output,400,"Invalid path",null); return;
            }
            if (!path.startsWith(prefix)) { error(output,404,"Not found",null); return; }
            String asset = path.substring(prefix.length()); if (asset.isEmpty()) asset = "index.html";
            long length = assets.length(asset);
            if (length < 0) { error(output,404,"Not found",null); return; }
            long start = 0, end = length-1; String range = headers.get("range");
            if (range != null) {
                try {
                    if (!range.matches("bytes=[0-9]*-[0-9]*")) throw new IllegalArgumentException();
                    String[] span = range.substring(6).split("-",-1);
                    if (span[0].isEmpty()) { long suffix=Long.parseLong(span[1]); if (suffix<=0) throw new IllegalArgumentException(); start=Math.max(0,length-suffix); }
                    else { start=Long.parseLong(span[0]); if (!span[1].isEmpty()) end=Math.min(end,Long.parseLong(span[1])); }
                    if (start < 0 || start >= length || end < start) throw new IllegalArgumentException();
                } catch (IllegalArgumentException bad) { error(output,416,"Invalid range","Content-Range: bytes */"+length+"\r\n"); return; }
            }
            long count = range == null ? length : end-start+1;
            String extra = range == null ? "" : "Content-Range: bytes "+start+"-"+end+"/"+length+"\r\n";
            String response = "HTTP/1.1 "+(range==null?"200 OK":"206 Partial Content")+"\r\nContent-Type: "+mime(asset)+"\r\nContent-Length: "+count+"\r\n"+
                "Accept-Ranges: bytes\r\nConnection: close\r\nCache-Control: no-cache\r\nX-Content-Type-Options: nosniff\r\n"+
                "Cross-Origin-Opener-Policy: same-origin\r\nCross-Origin-Embedder-Policy: require-corp\r\nCross-Origin-Resource-Policy: same-origin\r\n"+extra+"\r\n";
            output.write(response.getBytes(StandardCharsets.US_ASCII));
            if (!head && count > 0) {
                try (InputStream file = assets.open(asset)) {
                    while (start > 0) { long skipped=file.skip(start); if (skipped <= 0) { if (file.read()==-1) throw new EOFException(); skipped=1; } start-=skipped; }
                    byte[] buffer = new byte[65536];
                    while (count>0 && !closed) { int n=file.read(buffer,0,(int)Math.min(buffer.length,count)); if (n<0) throw new EOFException(); output.write(buffer,0,n); count-=n; }
                }
            }
            output.flush();
        } catch (IOException ignored) { /* A closed browser request is not an app crash. */ }
        finally { clients.remove(client); }
    }
    private static void error(OutputStream output,int status,String message,String extra) throws IOException {
        byte[] body=message.getBytes(StandardCharsets.UTF_8);
        output.write(("HTTP/1.1 "+status+" "+message+"\r\nConnection: close\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: "+body.length+"\r\n"+(extra==null?"":extra)+"\r\n").getBytes(StandardCharsets.US_ASCII));
        output.write(body);output.flush();
    }
    private static String mime(String path) {
        if (path.endsWith(".html")) return "text/html; charset=utf-8";
        if (path.endsWith(".js")) return "text/javascript; charset=utf-8";
        if (path.endsWith(".css")) return "text/css; charset=utf-8";
        if (path.endsWith(".wasm")) return "application/wasm";
        if (path.endsWith(".glb")) return "model/gltf-binary";
        if (path.endsWith(".json")) return "application/json";
        if (path.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }
    @Override public synchronized void close() {
        if (closed) return;closed=true;
        try { socket.close(); } catch (IOException ignored) {}
        for (Socket client:clients) try { client.close(); } catch (IOException ignored) {}
        clients.clear();workers.shutdownNow();
    }
}
