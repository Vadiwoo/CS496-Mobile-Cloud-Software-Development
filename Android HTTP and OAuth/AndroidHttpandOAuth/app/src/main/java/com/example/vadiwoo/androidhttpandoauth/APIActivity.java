package com.example.vadiwoo.androidhttpandoauth;

/**
 * Created by Vadiwoo on 2/27/2018.
 * Reference : https://gist.github.com/wolfordj/29353e87cebd97fe1cf13c1ae4b3c7fb
 */

import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleAdapter;

import net.openid.appauth.AuthState;
import net.openid.appauth.AuthorizationException;
import net.openid.appauth.AuthorizationRequest;
import net.openid.appauth.AuthorizationService;
import net.openid.appauth.AuthorizationServiceConfiguration;
import net.openid.appauth.ResponseTypeValues;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

        public class APIActivity extends AppCompatActivity {

            private AuthorizationService mAuthorizationService;
            private AuthState mAuthState;
            private OkHttpClient mOkHttpClient;
            public static final MediaType JSON
                    = MediaType.parse("application/json; charset=utf-8");

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                SharedPreferences authPreference = getSharedPreferences("auth", MODE_PRIVATE);
                setContentView(R.layout.activity_api);
                mAuthorizationService = new AuthorizationService(this);
                ((Button)findViewById(R.id.google_plus_get_post_button)).setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        try{
                            mAuthState.performActionWithFreshTokens(mAuthorizationService, new AuthState.AuthStateAction() {
                                @Override
                                public void execute(@Nullable String accessToken, @Nullable String idToken, @Nullable AuthorizationException e) {
                                    if(e == null){
                                        mOkHttpClient = new OkHttpClient();
                                        HttpUrl reqUrl = HttpUrl.parse("https://www.googleapis.com/plusDomains/v1/people/me/activities/user");
                                        reqUrl = reqUrl.newBuilder().addQueryParameter("key", "AIzaSyA9KlseleE7PQSvAi2Qya2GHQ4fxMIzObM").build();
                                        Request request = new Request.Builder()
                                                .url(reqUrl)
                                                .addHeader("Authorization", "Bearer " + accessToken)
                                                .build();
                                        mOkHttpClient.newCall(request).enqueue(new Callback() {
                                            @Override
                                            public void onFailure(Call call, IOException e) {
                                                e.printStackTrace();
                                            }

                                            @Override
                                            public void onResponse(Call call, Response response) throws IOException {
                                                String r = response.body().string();
                                                try {
                                                    JSONObject j = new JSONObject(r);
                                                    JSONArray items = j.getJSONArray("items");
                                                    List<Map<String,String>> posts = new ArrayList<Map<String,String>>();
                                                    for(int i = 0; i < 3; i++){
                                                        HashMap<String, String> m = new HashMap<String, String>();
                                                        m.put("published", items.getJSONObject(i).getString("published"));
                                                        m.put("title",items.getJSONObject(i).getString("title"));
                                                        posts.add(m);
                                                    }
                                                    final SimpleAdapter postAdapter = new SimpleAdapter(
                                                            APIActivity.this,
                                                            posts,
                                                            R.layout.google_plus_posts,
                                                            new String[]{"published", "title"},
                                                            new int[]{R.id.google_plus_posts_date_text, R.id.google_plus_posts_text});
                                                    runOnUiThread(new Runnable() {
                                                        @Override
                                                        public void run() {
                                                            ((ListView)findViewById(R.id.google_post_list)).setAdapter(postAdapter);
                                                        }
                                                    });
                                                } catch (JSONException e1) {
                                                    e1.printStackTrace();
                                                }

                                            }
                                        });
                                    }
                                }
                            });
                        } catch(Exception e){
                            e.printStackTrace();
                        }
                    }
                });

                ((Button)findViewById(R.id.google_plus_create_post_button)).setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        try{
                            mAuthState.performActionWithFreshTokens(mAuthorizationService, new AuthState.AuthStateAction() {
                                @Override
                                public void execute(@Nullable String accessToken, @Nullable String idToken, @Nullable AuthorizationException e) {
                                    if(e == null){
                                        EditText mEdit;
                                        mEdit = (EditText)findViewById(R.id.google_plus_post_message);
                                        String userInput = mEdit.getText().toString();
                                        String json = "{'object': {'originalContent': '" + userInput + "'},'access': {'domainRestricted': true}}";
                                        mOkHttpClient = new OkHttpClient();
                                        HttpUrl reqUrl = HttpUrl.parse("https://www.googleapis.com/plusDomains/v1/people/me/activities");
                                        reqUrl = reqUrl.newBuilder().addQueryParameter("key", "AIzaSyA9KlseleE7PQSvAi2Qya2GHQ4fxMIzObM").build();
                                        RequestBody body = RequestBody.create(JSON, json);
                                        Request request = new Request.Builder()
                                                .url(reqUrl)
                                                .post(body)
                                                .addHeader("Authorization", "Bearer " + accessToken)
                                                .build();
                                        mOkHttpClient.newCall(request).enqueue(new Callback() {
                                            @Override
                                            public void onFailure(Call call, IOException e) {
                                                e.printStackTrace();
                                            }

                                            @Override
                                            public void onResponse(Call call, Response response) throws IOException {
                                                String r = response.body().string();
                                                //System.out.println(r);
                                            }
                                        });
                                    }
                                }
                            });
                        } catch(Exception e){
                            e.printStackTrace();
                        }
                    }
                });
            }

            @Override
            protected void onStart(){
                mAuthState = getOrCreateAuthState();
                super.onStart();

            }

            AuthState getOrCreateAuthState(){
                AuthState auth = null;
                SharedPreferences authPreference = getSharedPreferences("auth", MODE_PRIVATE);
                String stateJson = authPreference.getString("stateJson", null);
                if(stateJson != null){
                    try {
                        auth = AuthState.jsonDeserialize(stateJson);
                    } catch (JSONException e) {
                        e.printStackTrace();
                        return null;
                    }
                }
                if( auth != null && auth.getAccessToken() != null){
                    return auth;
                } else {
                    updateAuthState();
                    return null;
                }
            }

            void updateAuthState(){

                Uri authEndpoint = new Uri.Builder().scheme("https").authority("accounts.google.com").path("/o/oauth2/v2/auth").build();
                Uri tokenEndpoint = new Uri.Builder().scheme("https").authority("www.googleapis.com").path("/oauth2/v4/token").build();
                Uri redirect = new Uri.Builder().scheme("com.example.vadiwoo.androidhttpandoauth").path("foo").build();

                AuthorizationServiceConfiguration config = new AuthorizationServiceConfiguration(authEndpoint, tokenEndpoint, null);
                AuthorizationRequest req = new AuthorizationRequest.Builder(config, "1098197557510-hup6r4lbrrdrlbhlqeg7blnc8s9pn3up.apps.googleusercontent.com", ResponseTypeValues.CODE, redirect)
                        .setScopes("https://www.googleapis.com/auth/plus.me", "https://www.googleapis.com/auth/plus.stream.write", "https://www.googleapis.com/auth/plus.stream.read")
                        .build();

        Intent authComplete = new Intent(this, AuthCompleteActivity.class);
        mAuthorizationService.performAuthorizationRequest(req, PendingIntent.getActivity(this, req.hashCode(), authComplete, 0));
    }
}