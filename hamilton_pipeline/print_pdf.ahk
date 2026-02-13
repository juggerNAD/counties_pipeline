; Wait for Chrome window with PDF to be active
WinWaitActive, ahk_exe chrome.exe

; Open print dialog
Send, ^p
Sleep, 1000

; Press Enter to select "Save as PDF"
Send, {Enter}
Sleep, 1000

; Construct full path to save PDF
; A_Args[1] contains the first argument passed from Python
downloadFolder := "C:\Users\juggernad\Desktop\PythonScrapingProject\HamiltonScraperApp\downloads"
pdfPath := downloadFolder . "\" . A_Args[1] . ".pdf"

; Send the full path
Send, %pdfPath%
Sleep, 500

; Press Enter to save
Send, {Enter}
Sleep, 4000  ; give Chrome enough time

; Close print dialog
Send, {Esc}
