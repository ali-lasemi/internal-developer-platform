# Control Plane Architecture

## Overview

The control plane provides orchestration between platform products.


## Main Components

API Gateway

Receives platform requests.


Resource Manager

Manages platform entities.


Workflow Coordinator

Triggers and tracks workflows.


State Manager

Maintains platform information.


Integration Layer

Communicates with external systems.


## Internal Connections

Developer Portal

connects to

Control Plane


Control Plane

connects to

Platform Services


Platform Services

connect to

Runtime Systems


## Architecture Principles

- Single platform entry point
- Domain based design
- Automation first
- Observable operations
