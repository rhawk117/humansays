#!/usr/bin/env bash

_in_actions() {
  [[ "${CI:-false}" == "true" ]]
}

_COLOR_RED='\033[0;31m'
_COLOR_GREEN='\033[0;32m'
_COLOR_YELLOW='\033[1;33m'
_COLOR_BLUE='\033[0;34m'
_COLOR_CYAN='\033[0;36m'
_COLOR_BOLD='\033[1m'
_COLOR_RESET='\033[0m'

log_info() {
  if _in_actions; then
    printf '%s\n' "::info::$*"
  else
    printf '%b  %s\n' "${_COLOR_BLUE}  info${_COLOR_RESET}" "$*"
  fi
}

log_success() {
  if _in_actions; then
    printf '%s\n' "::notice::$*"
  else
    printf '%b  %s\n' "${_COLOR_GREEN}    ok${_COLOR_RESET}" "$*"
  fi
}

log_warn() {
  if _in_actions; then
    printf '%s\n' "::warning::$*"
  else
    printf '%b  %s\n' "${_COLOR_YELLOW}  warn${_COLOR_RESET}" "$*" >&2
  fi
}

log_error() {
  if _in_actions; then
    printf '%s\n' "::error::$*"
  else
    printf '%b  %s\n' "${_COLOR_RED} error${_COLOR_RESET}" "$*" >&2
  fi
}

log_step() {
  if _in_actions; then
    printf '%s\n' "::group::$*"
  else
    printf '\n%b %s%b\n' "${_COLOR_BOLD}${_COLOR_CYAN}▶" "$*" "${_COLOR_RESET}"
  fi
}

log_step_end() {
  if _in_actions; then
    printf '%s\n' "::endgroup::"
  fi
}