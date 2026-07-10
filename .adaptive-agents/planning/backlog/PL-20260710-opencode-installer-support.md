# PL-20260710: OpenCode Installer Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-10

## Objective

Update the Adaptive Agents VS Code installer (scripts and vscode/) to detect, generate, and manage OpenCode configuration files alongside or instead of the current GitHub Copilot-specific integration.

## Problem Spec

The current installer produces VS Code settings and GitHub Copilot-specific instructions for discovering the Adaptive Agents repository. OpenCode is an emerging open standard for AI coding tool interop that provides a model-agnostic configuration layer. Without OpenCode support, users who prefer OpenCode-compatible editors or want editor-agnostic agent discovery are left out, and the installer produces Copilot-locked output.

## Scope

Detect whether the target environment supports OpenCode; generate appropriate OpenCode configuration (e.g. `.opencode.json` or equivalent) that points to the Adaptive Agents repository; optionally maintain Copilot support as a fallback. Exact configuration format and installation mechanism to be determined during activation. Full SDD specification will be written during activation.
