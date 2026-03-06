-- Hammerspoon Push-to-Talk Configuration
-- Option+Space = Push-to-Talk für Claude Code

local pttPidFile = os.getenv("HOME") .. "/.claude/scripts/ptt.pid"
local isRecording = false

-- Read PID from file
local function getPttPid()
    local f = io.open(pttPidFile, "r")
    if f then
        local pid = f:read("*all")
        f:close()
        return tonumber(pid)
    end
    return nil
end

-- Send signal to push-to-talk process
local function sendSignal(sig)
    local pid = getPttPid()
    if pid then
        os.execute("kill -" .. sig .. " " .. pid)
        return true
    else
        hs.alert.show("⚠️ Push-to-Talk nicht aktiv\nStarte: ptt")
        return false
    end
end

-- Key down handler (start recording)
local function onKeyDown()
    if not isRecording then
        isRecording = true
        sendSignal("USR1")
    end
end

-- Key up handler (stop recording)
local function onKeyUp()
    if isRecording then
        isRecording = false
        sendSignal("USR2")
    end
end

-- Bind Option+Space
local pttHotkey = hs.hotkey.bind({"alt"}, "space", onKeyDown, onKeyUp)

-- Notification on reload
hs.alert.show("Hammerspoon: Option+Space=PTT | Ctrl+Space=Skilldex")

-- Skilldex: Ctrl+Space = floating skill finder
-- Opens a small terminal, runs fzf, copies /skill <name> to clipboard
hs.hotkey.bind({"ctrl"}, "space", function()
    local script = os.getenv("HOME") .. "/.claude/bin/skilldex.sh"
    local wrapper = os.getenv("HOME") .. "/.claude/bin/skilldex-popup.sh"
    hs.task.new("/bin/bash", nil, {wrapper}):start()
end)

-- Auto-reload config on change
function reloadConfig(files)
    local doReload = false
    for _, file in pairs(files) do
        if file:sub(-4) == ".lua" then
            doReload = true
        end
    end
    if doReload then
        hs.reload()
    end
end
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
