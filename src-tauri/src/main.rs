#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// Tauri v2 container shell wrapper for FATE Core Menu-Bar System Tray Launcher

fn main() {
    tauri::Builder::default()
        .setup(|_app| {
            println!("[TAURI SYSTEM TRAY] FATE Desktop Menu-Bar Wrapper initialized.");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
