use serde::Serialize;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, State};

// ─── App State ─────────────────────────────────────────────────────────────

struct AppState {
    api_port: u16,
    api_process: Mutex<Option<Child>>,
    ollama_process: Mutex<Option<Child>>,
}

// ─── Helper: find Python ────────────────────────────────────────────────────

fn find_python() -> Option<String> {
    let candidates = [
        "python3",
        "python",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
        "/usr/bin/python3",
    ];
    for cmd in candidates {
        if Command::new(cmd)
            .arg("--version")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok()
        {
            return Some(cmd.to_string());
        }
    }
    None
}

fn find_ollama() -> &'static str {
    if std::path::Path::new("/usr/local/bin/ollama").exists() {
        "/usr/local/bin/ollama"
    } else if std::path::Path::new("/opt/homebrew/bin/ollama").exists() {
        "/opt/homebrew/bin/ollama"
    } else {
        "ollama"
    }
}

// ─── Auto-start backend ─────────────────────────────────────────────────────

fn start_api_backend(port: u16, resource_dir: &std::path::Path) -> Option<Child> {
    let python = match find_python() {
        Some(p) => p,
        None => {
            eprintln!("[LGPD] Python not found, API will not auto-start");
            return None;
        }
    };

    let backend_dir = resource_dir.join("backend");
    let venv_dir = dirs::data_local_dir()
        .unwrap_or_else(|| std::path::PathBuf::from("/tmp"))
        .join("lgpd-sentinel")
        .join("venv");

    // Create venv if it doesn't exist
    if !venv_dir.join("bin").join("python3").exists() {
        eprintln!("[LGPD] Creating Python venv at {:?}", venv_dir);
        let _ = Command::new(&python)
            .args(["-m", "venv", venv_dir.to_str().unwrap_or("/tmp/lgpd-venv")])
            .status();
    }

    let venv_python = venv_dir.join("bin").join("python3");
    let venv_pip = venv_dir.join("bin").join("pip");

    // Install dependencies if requirements.txt exists
    let req_file = backend_dir.join("requirements.txt");
    if req_file.exists() {
        // Check if uvicorn is already installed
        let check = Command::new(&venv_python)
            .args(["-c", "import uvicorn"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();

        if check.map(|s| !s.success()).unwrap_or(true) {
            eprintln!("[LGPD] Installing Python dependencies...");
            let _ = Command::new(&venv_pip)
                .args(["install", "-q", "-r", req_file.to_str().unwrap_or("")])
                .stdout(Stdio::null())
                .stderr(Stdio::piped())
                .status();
        }
    }

    // Start uvicorn
    eprintln!("[LGPD] Starting API on port {}", port);
    let child = Command::new(&venv_python)
        .args([
            "-m", "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", &port.to_string(),
        ])
        .env("PYTHONPATH", backend_dir.parent().unwrap_or(&backend_dir))
        .current_dir(&backend_dir)
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn();

    match child {
        Ok(c) => {
            eprintln!("[LGPD] API process started (PID: {})", c.id());
            Some(c)
        }
        Err(e) => {
            eprintln!("[LGPD] Failed to start API: {}", e);
            None
        }
    }
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

    let api_ready = reqwest::get(format!("http://localhost:{}/health", port))
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);

    let ollama_ready = reqwest::get("http://localhost:11434/api/tags")
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);

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
    if reqwest::get("http://localhost:11434/api/tags")
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false)
    {
        return Ok(true);
    }

    let ollama_bin = find_ollama();
    let child = Command::new(ollama_bin)
        .arg("serve")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to start Ollama: {}", e))?;

    *state.ollama_process.lock().unwrap() = Some(child);

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
    let api_port = portpicker::pick_unused_port().unwrap_or(8000);

    let state = AppState {
        api_port,
        api_process: Mutex::new(None),
        ollama_process: Mutex::new(None),
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(state)
        .setup(move |app| {
            // Auto-start API backend on app launch
            let resource_path = app.path().resource_dir()
                .unwrap_or_else(|_| std::path::PathBuf::from("."));

            let state = app.state::<AppState>();
            if let Some(child) = start_api_backend(api_port, &resource_path) {
                *state.api_process.lock().unwrap() = Some(child);
            }

            // Auto-start Ollama if installed
            let ollama_bin = find_ollama();
            if std::path::Path::new(ollama_bin).exists() || which::which("ollama").is_ok() {
                let child = Command::new(ollama_bin)
                    .arg("serve")
                    .stdout(Stdio::null())
                    .stderr(Stdio::null())
                    .spawn();
                if let Ok(c) = child {
                    eprintln!("[LGPD] Ollama auto-started (PID: {})", c.id());
                    *state.ollama_process.lock().unwrap() = Some(c);
                }
            }

            Ok(())
        })
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
