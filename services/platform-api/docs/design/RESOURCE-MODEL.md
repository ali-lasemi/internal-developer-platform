# Platform API Resource Model

## Core Resources

## Service

Represents an application managed by the platform.

Attributes:

- id
- name
- owner
- repository
- lifecycle
- environments


## Template

Represents a reusable application blueprint.

Attributes:

- id
- name
- version
- type


## Environment

Represents a deployment target.

Examples:

- development
- staging
- production


## Deployment

Represents an application delivery event.

Attributes:

- service
- version
- status
- timestamp


## API Principles

- Resource oriented design
- Versioned APIs
- Clear ownership
- Automation friendly
