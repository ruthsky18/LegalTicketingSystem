# Running Website in Cursor/VS Code

## Quick Start

### Option 1: Using Terminal (Current)
The server is already running! Simply:
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: "Simple Browser: Show"
3. Enter URL: `http://127.0.0.1:8000`

### Option 2: Using Task Runner
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
2. Type: "Tasks: Run Task"
3. Select: "Django: Run Server"
4. Then select: "Django: Open in Browser"

### Option 3: Using Debug (Recommended for Development)
1. Press `F5` or go to Run and Debug
2. Select "Python: Django" from the dropdown
3. The server will start and you can use Simple Browser to view

## Built-in Browser Preview

Cursor/VS Code has a built-in "Simple Browser" that you can use:

1. **Open Simple Browser:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
   - Type: `Simple Browser: Show`
   - Enter: `http://127.0.0.1:8000`

2. **Or use keyboard shortcut:**
   - The Simple Browser extension allows you to view web pages directly in VS Code/Cursor

## Live Editing Workflow

1. **Edit files** in the editor (templates, CSS, Python files)
2. **Save the file** (`Ctrl+S`)
3. **Refresh the Simple Browser** view (or it auto-refreshes)
4. Changes appear immediately!

## Tips

- Keep the Simple Browser open side-by-side with your code
- Use split view: code on left, browser on right
- Django auto-reloads on Python file changes
- For template/CSS changes, just refresh the browser

## Stopping the Server

- Press `Ctrl+C` in the terminal where the server is running
- Or use the stop button in the Debug panel

