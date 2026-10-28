package io.github.deimerjr.dshmobile;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(OpenUrlPlugin.class);
        super.onCreate(savedInstanceState);
    }
}