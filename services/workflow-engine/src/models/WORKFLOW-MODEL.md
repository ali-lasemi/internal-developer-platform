# Workflow Domain Model

## Workflow

Represents an automated platform process.


Attributes:

- Name
- Version
- Owner
- Steps
- Status


## Workflow Execution

Represents one workflow run.


Attributes:

- Workflow
- Started time
- Completed time
- Result
- Logs


## Workflow Step

Represents an individual operation.


Examples:

- Create repository
- Generate files
- Deploy service
- Send notification


## Execution States

Created

Queued

Running

Completed

Failed

Cancelled
