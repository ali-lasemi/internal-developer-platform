# Service Domain Model

## Service Entity

Represents an application managed by the platform.

## Attributes

id

Unique identifier.

name

Service name.

owner

Responsible team.

repository

Source repository.

lifecycle

Current lifecycle state.

environment

Runtime environments.


## Relationships

Service belongs to Team.

Service uses Template.

Service creates Deployments.
