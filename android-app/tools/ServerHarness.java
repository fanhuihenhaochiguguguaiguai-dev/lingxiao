package com.yaojing.lingyuan;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.zip.*;

/** Runs the actual compiled AssetServer class against the APK, without Android mocks. */
public final class ServerHarness {
    public static void main(String[] args) throws Exception {
        try (ZipFile apk=new ZipFile(args[0])) {
            final Map<String,Long> sizes=new HashMap<>();
            try (BufferedReader reader=new BufferedReader(new InputStreamReader(apk.getInputStream(apk.getEntry("assets/web-inventory.tsv")),StandardCharsets.UTF_8))) {
                String line;while ((line=reader.readLine())!=null) { String[] fields=line.split("\t");sizes.put(fields[0],Long.parseLong(fields[1])); }
            }
            try (AssetServer server=new AssetServer(new AssetServer.Assets() {
                public InputStream open(String path) throws IOException { return apk.getInputStream(apk.getEntry("assets/web/"+path)); }
                public long length(String path) { Long length=sizes.get(path);return length==null?-1:length; }
            })) {
                // The session URL stays within the local verifier, never in a report.
                System.out.println(server.url());System.out.flush();
                while (System.in.read()!=-1) {}
            }
        }
    }
}
