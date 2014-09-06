package com.cotosho.minosaur.datefinder;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;

import com.cotosho.minosaur.R;
import com.cotosho.minosaur.settings.SettingsActivity;


public class MainActivity extends Activity {
    public static final String PREFS_NAME = "BlindatePrefsFile";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        SharedPreferences settings = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        if (!settings.getBoolean(SettingsActivity.IS_SETUP_KEY, false)) {
            startSettingsActivity();
        } else {
            setContentView(R.layout.activity_main);
        }
    }

    private void startSettingsActivity() {
        Intent intent = new Intent(this, SettingsActivity.class);
        startActivity(intent);

    }
}
