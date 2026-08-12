# Event Platform

## Purpose

The Event Platform provides asynchronous communication for the Internal Developer Platform.

It allows platform capabilities to publish domain events without tightly coupling services together.

## MVP Capabilities

- Publish platform events
- Validate event payloads
- Return event identifiers
- Prepare event-driven integrations

## Initial Event Types

- service.created
- service.registered
- workflow.started
- workflow.completed
- workflow.failed
- policy.evaluated
- identity.created
