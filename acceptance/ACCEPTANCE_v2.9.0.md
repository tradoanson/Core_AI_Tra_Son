# v2.9.0 Release Candidate

Status pending CI. Candidate gate requires independently supplied evidence for Linux Python 3.11/3.12/3.13, Windows native tests, wheel SHA-256, Windows EXE artifact, synthetic decision quality and security review. No evidence is assumed from merely running the gate. CI builds a PyInstaller onefile Windows EXE and publishes it as a workflow artifact; this does not prove the EXE launches successfully on a clean Windows machine or qualifies for production. At least 473 unit tests expected. Offline synthetic SHADOW only.
