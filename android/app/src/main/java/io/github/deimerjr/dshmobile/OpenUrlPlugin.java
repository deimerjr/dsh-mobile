package io.github.deimerjr.dshmobile;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Navigates the app WebView to a remote URL from the native side.
 * A browser-initiated navigation sends SameSite=Strict cookies that a page-initiated
 * cross-site navigation (DSH uses SameSite=Strict) would drop.
 */
@CapacitorPlugin(name = "OpenUrl")
public class OpenUrlPlugin extends Plugin {

    @PluginMethod
    public void open(PluginCall call) {
        String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("url is required");
            return;
        }
        getActivity().runOnUiThread(() -> {
            getBridge().getWebView().loadUrl(url);
            call.resolve();
        });
    }

    @PluginMethod
    public void reload(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            getBridge().getWebView().loadUrl("https://localhost");
            call.resolve();
        });
    }
}