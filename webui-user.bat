@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--use-directml --opt-sdp-attention --upcast-sampling --opt-channelslast

call webui.bat
