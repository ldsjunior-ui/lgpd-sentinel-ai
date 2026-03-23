use serde::Serialize;
use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::State;

// ─── App State ─────────────────────────────────────────────────────────────

struct AppState {
    api_port: u16,
    api_process: Mutex<Option<Child>>,
    ollama_process: Mutex<Option<Child>>,
}

// ─── IPC Commands ──────────────────────────────────────────────────────────

#[derive(Serialize)]
struct StatusResponse {
    api_ready: bool,
    api_port: u16,
    ollama_ready: bool,
    model_available: bool,
}

#[tauri::command]
fn get_api_port(state: State<AppState>) -> u16 {
    state.api_port
}

#[tauri::command]
async fn get_status(state: State<'_, AppState>) -> Result<StatusResponse, String> {
    let port = state.api_port;

    // Check API health
    let api_ready = reqwest::get(format!("http://localhost:{}/health", port))
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);

    // Check Ollama
    let ollama_ready = reqwest::get("http://localhost:11434/api/tags")
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);

    // Check if model is available
    let model_available = if ollama_ready {
        match reqwest::get("http://localhost:11434/api/tags").await {
            Ok(resp) => resp.text().await.unwrap_or_default().contains("mistral"),
            Err(_) => false,
        }
    } else {
        false
    };

    Ok(StatusResponse {
        api_ready,
        api_port: port,
        ollama_ready,
        model_available,
    })
}

#[tauri::command]
fn check_ollama_installed() -> bool {
    // Check PATH first, then common install locations
    which::which("ollama").is_ok()
        || std::path::Path::new("/usr/local/bin/ollama").exists()
        || std::path::Path::new("/opt/homebrew/bin/ollama").exists()
        || std::path::Path::new(&format!(
            "{}/bin/ollama",
            std::env::var("HOME").unwrap_or_default()
        ))
        .exists()
}

#[tauri::command]
async fn start_ollama(state: State<'_, AppState>) -> Result<bool, String> {
    // Check if already running
    if reqwest::get("http://localhost:11434/api/tags")
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false)
    {
        return Ok(true);
    }

    // Find ollama binary
    let ollama_bin = if std::path::Path::new("/usr/local/bin/ollama").exists() {
        "/usr/local/bin/ollama"
    } else if std::path::Path::new("/opt/homebrew/bin/ollama").exists() {
        "/opt/homebrew/bin/ollama"
    } else {
        "ollama"
    };

    // Start ollama serve
    let child = Command::new(ollama_bin)
        .arg("serve")
        .spawn()
        .map_err(|e| format!("Failed to start Ollama: {}", e))?;

    *state.ollama_process.lock().unwrap() = Some(child);

    // Wait for it to be ready (up to 30s)
    for _ in 0..60 {
        tokio::time::sleep(std::time::Duration::from_millis(500)).await;
        if reqwest::get("http://localhost:11434/api/tags")
            .await
            .map(|r| r.status().is_success())
            .unwrap_or(false)
        {
            return Ok(true);
        }
    }

    Err("Ollama failed to start within 30 seconds".into())
}

#[tauri::command]
async fn pull_model(model: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post("http://localhost:11434/api/pull")
        .json(&serde_json::json!({ "name": model }))
        .send()
        .await
        .map_err(|e| format!("Pull request failed: {}", e))?;

    let text = resp
        .text()
        .await
        .map_err(|e| format!("Failed to read response: {}", e))?;

    Ok(text)
}

// ─── Tauri App Setup ───────────────────────────────────────────────────────

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Find an available port for the FastAPI backend
    let api_port = portpicker::pick_unused_port().unwrap_or(8000);

    let state = AppState {
        api_port,
        api_process: Mutex::new(None),
        ollama_process: Mutex::new(None),
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(state)
        .invoke_handler(tauri::generate_handler![
            get_api_port,
            get_status,
            check_ollama_installed,
            start_ollama,
            pull_model,
        ])
        .run(tauri::generate_context!())
        .expect("error while running LGPD Sentinel AI");
}
