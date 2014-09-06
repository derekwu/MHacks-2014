package com.cotosho.minosaur.settings;

import android.app.Activity;
import android.os.Bundle;

import com.cotosho.minosaur.R;

/**
 * Created by derekwu on 9/6/14.
 */
public class SettingsActivity extends Activity{
    public static final String IS_SETUP_KEY = "isSetup";
    public static final String FIRST_NAME_KEY = "firstName";
    public static final String LAST_NAME_KEY = "lastName";
    public static final String AGE_KEY = "age";
    public static final String GENDER_KEY = "gender";
    public static final String SEXUAL_ORIENTATION_KEY = "sexualOrientation";
    public static final String PRICE_KEY = "price";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
    }


}
