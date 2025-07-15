# Task Namespaces Documentation

This document provides an overview of all available task namespaces in the XO Core project.

## Core Tasks

### ✅ pulse

**Module:** `xo_core.fab_tasks.pulse_tasks`

**Description:** Pulse-related tasks for content management

**Status:** Not available

### ✅ vault

**Module:** `xo_core.fab_tasks.vault_tasks`

**Description:** Vault-related tasks for secure storage

**Status:** Not available

### ✅ summary

**Module:** `xo_core.fab_tasks.summary_tasks`

**Description:** Task summary and documentation generation

**Status:** Not available

### ✅ validate_tasks

**Module:** `xo_core.fab_tasks.validate_tasks`

**Description:** Task validation utilities

**Status:** Not available

## Ci Tasks

### ✅ cz-lint

**Module:** `xo_core.commitizen_tasks`

**Description:** Commitizen linting and checks

**Status:** Not available

## Content Tasks

### 📦 drop

**Module:** `xo_core.fab_tasks.drop_tasks`

**Description:** XO-Drop content management tasks

**Status:** Loaded

## Runtime Tasks

### 📦 runtime

**Module:** `xo_core.fab_tasks.runtime_tasks`

**Description:** Runtime environment management

**Status:** Not available

## Testing Tasks

### 📦 test

**Module:** `xo_core.fab_tasks.test_tasks`

**Description:** Testing and diagnostics tasks

**Status:** Not available

## Info Tasks

### 📦 namespace

**Module:** `xo_core.fab_tasks.info_tasks`

**Description:** Namespace information and documentation tasks

**Status:** Loaded

## External Tasks

### 📦 xo_agent

**Module:** `xo_agent.tasks`

**Description:** XO Agent integration tasks

**Status:** Loaded

### 📦 xo

**Module:** `xo_agent.tasks`

**Description:** XO Agent tasks (alias)

**Status:** Loaded

### 📦 agent0

**Module:** `agent0.tasks`

**Description:** Agent0 integration tasks

**Status:** Loaded

## Usage

To see all available tasks:
```bash
fab --list
```

To get detailed namespace information:
```bash
fab namespace.info
```
