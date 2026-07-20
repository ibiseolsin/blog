import SwiftUI
import WebKit
import AppKit

struct WebView: NSViewRepresentable {
    let url: URL

    func makeNSView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateNSView(_ nsView: WKWebView, context: Context) {}
}

func ensureServerRunning() {
    let url = URL(string: "http://localhost:8000/api/tasks")!
    var request = URLRequest(url: url)
    request.timeoutInterval = 2

    let semaphore = DispatchSemaphore(value: 0)
    var isUp = false
    URLSession.shared.dataTask(with: request) { _, response, _ in
        if let http = response as? HTTPURLResponse, http.statusCode == 200 {
            isUp = true
        }
        semaphore.signal()
    }.resume()
    _ = semaphore.wait(timeout: .now() + 3)

    if !isUp {
        let script = """
        tell application "Terminal"
            set w to do script "/Users/seonsuji/Desktop/hookingpoint/0720_todo/start_server.command"
            set miniaturized of (front window) to true
        end tell
        """
        if let appleScript = NSAppleScript(source: script) {
            var error: NSDictionary?
            appleScript.executeAndReturnError(&error)
        }
        Thread.sleep(forTimeInterval: 1.5)
    }
}

@main
struct MyTodoMenuBarApp: App {
    init() {
        ensureServerRunning()
    }

    var body: some Scene {
        MenuBarExtra("My Todo", systemImage: "checklist") {
            WebView(url: URL(string: "http://localhost:8000")!)
                .frame(width: 380, height: 520)
        }
        .menuBarExtraStyle(.window)
    }
}
